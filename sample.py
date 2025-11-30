# #!/usr/bin/env python
# import sys
# import os

# def main():
#     """Main function for script entry point"""
#     sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
#     try:
#         from src.main import main as server_main
#         server_main()
#     except Exception as e:
#         print(f"Error starting MCP server: {e}", file=sys.stderr)
#         sys.exit(1)

# if __name__ == "__main__":
#     main()