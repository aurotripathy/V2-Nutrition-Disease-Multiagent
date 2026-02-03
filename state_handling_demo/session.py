"""
Session management utilities
"""


async def verify_initial_state(session_service, app_name, user_id, session_id):
    """
    Verify that the initial state was set correctly for a session.
    
    Args:
        session_service: The session service instance
        app_name: Application name
        user_id: User ID
        session_id: Session ID
        
    Returns:
        bool: True if session was retrieved successfully, False otherwise
    """
    retrieved_session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    print("\n--- Initial Session State ---")
    if retrieved_session:
        print(retrieved_session.state)
        print(f"✅ Session '{session_id}' created for user '{user_id}' in app '{app_name}'.")
        return True
    else:
        print("Error: Could not retrieve session.")
        print(f"❌ Session '{session_id}' not found for user '{user_id}' in app '{app_name}'.")
        return False
