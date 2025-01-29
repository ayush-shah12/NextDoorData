import logfire
from keys import KEYS

logfire.configure(
    token=KEYS.Logfire.write_token, 
    scrubbing=False, 
    environment=KEYS.Logfire.environment,
)
