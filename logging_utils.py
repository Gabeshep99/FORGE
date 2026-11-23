"""Per-session append-only JSONL with secret redaction and in-memory export."""
import json, os, re, uuid
from datetime import datetime, timezone
from pathlib import Path

def redact(value):
    secret = os.getenv('OPENAI_API_KEY', '')
    if isinstance(value, dict):
        return {k: '[REDACTED]' if any(t in k.lower() for t in ('api_key','authorization','password','secret')) else redact(v) for k,v in value.items()}
    if isinstance(value, (list, tuple)): return [redact(v) for v in value]
    if isinstance(value, str):
        if secret: value = value.replace(secret, '[REDACTED]')
        return re.sub(r'\bsk-[A-Za-z0-9_-]{8,}', '[REDACTED]', value)
    return value

class AuditLog:
    def __init__(self, directory=None, session_id=None):
        self.session_id = session_id or str(uuid.uuid4())
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', self.session_id): raise ValueError('Invalid session identifier')
        self.directory = Path(directory or os.getenv('FORGE_LOG_DIR', 'logs'))
        self.events = []
        self.persistence_error = None

    def write(self, event, **data):
        entry = redact({'timestamp':datetime.now(timezone.utc).isoformat(), 'session_id':self.session_id, 'event':event, **data})
        self.events.append(entry)
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            fd = os.open(self.directory / f'{self.session_id}.jsonl', os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            with os.fdopen(fd, 'a', encoding='utf-8') as f: f.write(json.dumps(entry, ensure_ascii=False, default=str)+'\n')
        except OSError:
            self.persistence_error = 'Disk logging unavailable. Download the session log before closing this tab.'
        return entry

    def export(self):
        return json.dumps({'session_id':self.session_id, 'events':self.events}, indent=2, ensure_ascii=False, default=str)
