"""
NFL Draft Scouting Chatbot v9 - GUIDED RAG

PHILOSOPHY: Best of All Worlds
- Creative question understanding (like v8/MunchAI)
- Strict RAG data retrieval (like v7.1)
- Claude uses TOOLS to query database properly
- No hallucinations, no bad recommendations

Claude understands ANY question, but queries database with discipline.
"""

import anthropic
import chromadb
from chromadb.utils import embedding_functions
import json
import os
from typing import List, Dict, Optional



from dotenv import load_dotenv
load_dotenv() 


class GuidedRAGDraftScout:
    """
    Uses Claude's tool use to query database properly
    - Claude understands the question (creative)
    - Claude calls tools to get data (structured)
    - Claude answers using ONLY retrieved data (RAG)
    """
    
    def __init__(self, api_key: str = None, chroma_path: str = "./chroma_db",
                 team_needs_file: str = "nfl_team_needs_2026_ALL_TEAMS.json"):
        
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # ChromaDB
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_collection(
            name="nfl_draft_2026",
            embedding_function=embedding_function
        )
        
        # Team needs
        with open(team_needs_file, 'r') as f:
            raw_data = json.load(f)
            
        # Handle both JSON structures
        if 'nfl_teams_2026_draft' in raw_data:
            # New structure: convert teams array to dictionary
            teams_list = raw_data['nfl_teams_2026_draft']['teams']
            teams_dict = {}
            for team in teams_list:
                code = team['team_code']
                teams_dict[code] = {
                    'team_name': team['team_name'],
                    'record': team.get('season_context', {}).get('record', 'N/A'),
                    'tier': team.get('team_tier', 'N/A'),
                    'key_context': team.get('team_philosophy', ''),
                    # Handle single or multiple picks
                    'draft_pick_round_1': self._extract_pick(team.get('draft_capital', {}).get('round_1', {})),
                    'draft_pick_round_2': self._extract_pick(team.get('draft_capital', {}).get('round_2', {})),
                    'draft_pick_round_3': self._extract_pick(team.get('draft_capital', {}).get('round_3', {})),
                    'biggest_needs': []
                }
                if 'positional_needs' in team:
                    for need in team['positional_needs']:
                        teams_dict[code]['biggest_needs'].append({
                            'position': need['position'],
                            'priority': need['priority'],
                            'context': need['context']
                        })
            self.team_needs_data = {'teams': teams_dict}
        elif 'teams' in raw_data:
            # Old structure: already in correct format
            self.team_needs_data = raw_data
        else:
            raise ValueError("Invalid team needs JSON structure")
        
        # Initialize tools and conversation memory
        self._init_tools_and_memory()
    
    def _extract_pick(self, draft_round: Dict) -> str:
        """Extract pick number(s) from draft_capital round"""
        if not draft_round:
            return 'N/A'
        
        pick = draft_round.get('pick')
        if pick is None:
            return 'N/A'
        
        # Handle different pick formats
        if isinstance(pick, int):
            return str(pick)
        elif isinstance(pick, str):
            # "NONE", "13, 29", etc.
            return pick
        else:
            return str(pick)
        
    def _init_tools_and_memory(self):
        """Initialize tools and conversation memory"""
        self.position_aliases = {'LB': 'ILB'}
        self.conversation_history = []
        
        # Define tools for Claude
        self.tools = [
            {
                "name": "get_team_info",
                "description": "Get a team's draft pick, needs, and context. Use this whenever a team is mentioned.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "team_name": {
                            "type": "string",
                            "description": "Team name or abbreviation (e.g., 'Buccaneers', 'TB', 'Bucs')"
                        }
                    },
                    "required": ["team_name"]
                }
            },
            {
                "name": "get_prospects_by_position_and_rank",
                "description": "Get prospects at a specific position within a rank range. Use this to find prospects that match team needs at their draft position.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "position": {
                            "type": "string",
                            "description": "Position code (QB, RB, WR, TE, OT, OG, OC, EDGE, CB, S, ILB, DL3T)"
                        },
                        "min_rank": {
                            "type": "integer",
                            "description": "Minimum consensus rank (lower = better)"
                        },
                        "max_rank": {
                            "type": "integer",
                            "description": "Maximum consensus rank"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max number of results (default 10)",
                            "default": 10
                        }
                    },
                    "required": ["position", "min_rank", "max_rank"]
                }
            },
            {
                "name": "get_player_info",
                "description": "Get detailed information about a specific player by name.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "player_name": {
                            "type": "string",
                            "description": "Player's name (e.g., 'Fernando Mendoza', 'Jeremiyah Love')"
                        }
                    },
                    "required": ["player_name"]
                }
            }
        ]
        
        print("✅ Guided RAG Draft Scout v9 initialized")
        print(f"✅ Database: {self.collection.count()} prospects + 31 teams")
        print("🎯 GUIDED RAG: Creative understanding + Disciplined queries")
        print("    Claude uses tools to query database properly!\n")
    
    def chat(self, user_message: str) -> str:
        """
        Claude-guided RAG with conversation memory:
        1. Claude reads the question (with conversation context)
        2. Claude decides what tools to call
        3. Tools return database data
        4. Claude answers using ONLY that data
        """
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Call Claude with tools and full conversation history
        response = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            tools=self.tools,
            messages=self.conversation_history,
            system=self._get_system_prompt()
        )
        
        # Track assistant's response (including tool use)
        assistant_content = []
        
        # Process tool calls
        while response.stop_reason == "tool_use":
            # Collect tool uses
            for content_block in response.content:
                assistant_content.append(content_block)
            
            # Execute tools
            tool_results = []
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_result = self._execute_tool(content_block.name, content_block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": json.dumps(tool_result)
                    })
            
            # Add assistant message with tool uses
            self.conversation_history.append({"role": "assistant", "content": assistant_content})
            
            # Add tool results
            self.conversation_history.append({"role": "user", "content": tool_results})
            
            # Continue conversation
            assistant_content = []
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=3000,
                tools=self.tools,
                messages=self.conversation_history,
                system=self._get_system_prompt()
            )
        
        # Get final answer
        answer = ""
        for content_block in response.content:
            if hasattr(content_block, "text"):
                answer += content_block.text
                assistant_content.append(content_block)
        
        # Add final assistant response to history
        self.conversation_history.append({"role": "assistant", "content": assistant_content})
        
        return answer
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def _get_system_prompt(self) -> str:
        """System prompt for Claude"""
        return """You are an NFL Draft scout with database access through tools.

CONVERSATION MEMORY:
- You have access to the full conversation history
- When user says "those three" or "them", refer to previous context
- Be creative in understanding vague questions

HOW TO USE TOOLS:
1. When user asks about a team → call get_team_info first
2. Once you have team's pick + needs → call get_prospects_by_position_and_rank for EACH need
   - Use realistic rank ranges based on pick (pick #15 → look at ranks 5-55)
   - ONLY query positions that are in the team's needs list
   - Teams may have MULTIPLE picks in a round (e.g., "13, 29" or "2, 16")
3. When user asks about a player → call get_player_info
4. For creative/vague questions → make logical inferences and use tools creatively

EXAMPLES OF CREATIVE RESPONSES:
- "What position is very good?" → Query top prospects at each major position, compare depth
- "Show me sleepers" → Query prospects ranked 80-150 who have elite stats
- "Best of those three" → Refer to previous WRs mentioned, compare using available data
- "Need someone tall" → Query QBs, filter by height in your analysis

CRITICAL RULES:
- ONLY recommend prospects whose position matches team needs
- ONLY recommend prospects in realistic rank range for pick
- Use conversation history to understand vague references
- Be creative but always ground in database data
- Consensus rank: lower number = better
- NO EMOJIS
- Don't ask clarifying questions if you can infer from context
- When team has multiple picks (e.g., "13, 29"), recommend prospects for EACH pick

DRAFT LOGIC:
- Pick #15 should target ranks ~5-55 (can reach up 10, find value down 40)
- Round 1 = ranks 1-32, Round 2 = 33-64, Round 3 = 65-96, Round 4 = 97-128
- Day 3 = rounds 4-7 (ranks 97-250)
- VALUE = player ranked higher than pick (good)
- REACH = player ranked lower than pick (bad)

Use tools to get data, but be creative in understanding what the user wants!"""
    
    def _execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Execute a tool and return results"""
        
        if tool_name == "get_team_info":
            return self._tool_get_team_info(tool_input["team_name"])
        
        elif tool_name == "get_prospects_by_position_and_rank":
            position = tool_input["position"]
            min_rank = tool_input["min_rank"]
            max_rank = tool_input["max_rank"]
            limit = tool_input.get("limit", 10)
            return self._tool_get_prospects(position, min_rank, max_rank, limit)
        
        elif tool_name == "get_player_info":
            return self._tool_get_player(tool_input["player_name"])
        
        return {"error": "Unknown tool"}
    
    def _tool_get_team_info(self, team_name: str) -> Dict:
        """Tool: Get team information"""
        team_name_lower = team_name.lower()
        
        # Comprehensive team name mapping
        team_mappings = {
            # AFC East
            'bills': 'BUF', 'buffalo': 'BUF',
            'dolphins': 'MIA', 'miami': 'MIA',
            'patriots': 'NE', 'new england': 'NE', 'pats': 'NE',
            'jets': 'NYJ', 'new york jets': 'NYJ',
            
            # AFC North
            'ravens': 'BAL', 'baltimore': 'BAL',
            'bengals': 'CIN', 'cincinnati': 'CIN',
            'browns': 'CLE', 'cleveland': 'CLE',
            'steelers': 'PIT', 'pittsburgh': 'PIT',
            
            # AFC South
            'texans': 'HOU', 'houston': 'HOU',
            'colts': 'IND', 'indianapolis': 'IND', 'indy': 'IND',
            'jaguars': 'JAX', 'jacksonville': 'JAX', 'jags': 'JAX',
            'titans': 'TEN', 'tennessee': 'TEN',
            
            # AFC West
            'broncos': 'DEN', 'denver': 'DEN',
            'chiefs': 'KC', 'kansas city': 'KC', 'kc': 'KC',
            'raiders': 'LV', 'las vegas': 'LV', 'vegas': 'LV',
            'chargers': 'LAC', 'los angeles chargers': 'LAC', 'la chargers': 'LAC',
            
            # NFC East
            'cowboys': 'DAL', 'dallas': 'DAL',
            'giants': 'NYG', 'new york giants': 'NYG',
            'eagles': 'PHI', 'philadelphia': 'PHI', 'philly': 'PHI',
            'commanders': 'WAS', 'washington': 'WAS',
            
            # NFC North
            'bears': 'CHI', 'chicago': 'CHI',
            'lions': 'DET', 'detroit': 'DET',
            'packers': 'GB', 'green bay': 'GB',
            'vikings': 'MIN', 'minnesota': 'MIN',
            
            # NFC South
            'falcons': 'ATL', 'atlanta': 'ATL',
            'panthers': 'CAR', 'carolina': 'CAR',
            'saints': 'NO', 'new orleans': 'NO',
            'buccaneers': 'TB', 'tampa bay': 'TB', 'tampa': 'TB', 'bucs': 'TB',
            
            # NFC West
            'cardinals': 'ARI', 'arizona': 'ARI',
            'rams': 'LAR', 'los angeles rams': 'LAR', 'la rams': 'LAR',
            'seahawks': 'SEA', 'seattle': 'SEA',
            '49ers': 'SF', 'niners': 'SF', 'san francisco': 'SF',
        }
        
        # Try to find team code
        team_code = None
        
        # First check if it's already a team code
        if team_name.upper() in self.team_needs_data['teams']:
            team_code = team_name.upper()
        # Then check mappings
        elif team_name_lower in team_mappings:
            team_code = team_mappings[team_name_lower]
        # Finally check if team name contains a keyword
        else:
            for keyword, code in team_mappings.items():
                if keyword in team_name_lower:
                    team_code = code
                    break
        
        if not team_code or team_code not in self.team_needs_data['teams']:
            return {"error": f"Team '{team_name}' not found"}
        
        team = self.team_needs_data['teams'][team_code]
        
        return {
            "team_name": team['team_name'],
            "draft_pick": team.get('draft_pick_round_1', 'N/A'),
            "record": team.get('record', 'N/A'),
            "tier": team.get('tier', 'N/A'),
            "key_context": team.get('key_context', ''),
            "needs": team.get('biggest_needs', [])
        }
    
    def _tool_get_prospects(self, position: str, min_rank: int, max_rank: int, limit: int) -> Dict:
        """Tool: Get prospects by position and rank range"""
        
        # Handle position aliases
        query_position = self.position_aliases.get(position, position)
        
        # Query ChromaDB
        results = self.collection.query(
            query_texts=[f"{query_position} prospect"],
            n_results=100,
            where={
                "$and": [
                    {"position": query_position},
                    {"type": {"$ne": "team_needs"}}
                ]
            }
        )
        
        prospects = []
        if results['metadatas'] and results['metadatas'][0]:
            for i, metadata in enumerate(results['metadatas'][0]):
                consensus_rank = metadata.get('consensus_rank')
                if not consensus_rank or consensus_rank == 'N/A':
                    continue
                
                try:
                    rank_num = float(consensus_rank)
                except:
                    continue
                
                if min_rank <= rank_num <= max_rank:
                    stats = {}
                    if 'stats' in metadata and metadata['stats']:
                        try:
                            stats = json.loads(metadata['stats'])
                        except:
                            pass
                    
                    prospect = {
                        'name': metadata.get('name', 'Unknown'),
                        'position': metadata.get('position', 'N/A'),
                        'school': metadata.get('school', 'N/A'),
                        'height': metadata.get('height', 'N/A'),
                        'weight': metadata.get('weight', 'N/A'),
                        'consensus_rank': rank_num,
                        'stats': stats
                    }
                    prospects.append(prospect)
        
        prospects.sort(key=lambda x: x['consensus_rank'])
        return {"prospects": prospects[:limit]}
    
    def _tool_get_player(self, player_name: str) -> Dict:
        """Tool: Get player information"""
        results = self.collection.query(
            query_texts=[player_name],
            n_results=10,
            where={"type": {"$ne": "team_needs"}}
        )
        
        if not results['metadatas'] or not results['metadatas'][0]:
            return {"error": f"Player '{player_name}' not found"}
        
        # Find best match
        for i, metadata in enumerate(results['metadatas'][0]):
            stored_name = metadata.get('name', '').lower()
            search_name = player_name.lower()
            
            words_stored = set(stored_name.split())
            words_search = set(search_name.split())
            
            if words_stored == words_search or words_search.issubset(words_stored):
                stats = {}
                if 'stats' in metadata and metadata['stats']:
                    try:
                        stats = json.loads(metadata['stats'])
                    except:
                        pass
                
                return {
                    'name': metadata.get('name', 'Unknown'),
                    'position': metadata.get('position', 'N/A'),
                    'school': metadata.get('school', 'N/A'),
                    'height': metadata.get('height', 'N/A'),
                    'weight': metadata.get('weight', 'N/A'),
                    'consensus_rank': metadata.get('consensus_rank', 'N/A'),
                    'description': results['documents'][0][i],
                    'stats': stats
                }
        
        return {"error": f"Player '{player_name}' not found"}


def main():
    print("\n" + "="*60)
    print("GUIDED RAG NFL DRAFT SCOUT v9")
    print("="*60)
    print("\n🎯 Creative Understanding + Disciplined Queries")
    print("\nHow it works:")
    print("  1. You ask ANYTHING")
    print("  2. Claude figures out what data is needed")
    print("  3. Claude calls tools to query database properly")
    print("  4. Claude answers using ONLY retrieved data")
    print("\nResult: Creative + No hallucinations!")
    print("="*60 + "\n")
    
    scout = GuidedRAGDraftScout()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("\nGoodbye!")
                break
            
            print("\nScout: ", end="", flush=True)
            response = scout.chat(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()