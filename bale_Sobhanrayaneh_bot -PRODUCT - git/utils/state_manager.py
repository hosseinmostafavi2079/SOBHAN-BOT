class StateManager:
    """
    Manages user states for the Admin wizard flow.
    Structure: { user_id: { 'step': 'STEP_NAME', 'data': {...} } }
    """
    def __init__(self):
        self.storage = {}

    def get_step(self, user_id):
        return self.storage.get(user_id, {}).get('step', None)

    def set_step(self, user_id, step):
        if user_id not in self.storage:
            self.storage[user_id] = {'data': {}}
        self.storage[user_id]['step'] = step

    def update_data(self, user_id, key, value):
        if user_id in self.storage:
            self.storage[user_id]['data'][key] = value

    def get_data(self, user_id):
        return self.storage.get(user_id, {}).get('data', {})

    def clear_state(self, user_id):
        if user_id in self.storage:
            del self.storage[user_id]

# Global instance
state_manager = StateManager()