# Kimi CLI Interaction Research

## Key Findings

### Simplified Approach: `--print --yolo` Mode

Instead of using pexpect for interactive session management, Kimi CLI supports a **non-interactive mode** that's perfect for programmatic use:

```bash
kimi --print --yolo -c "your command here" -w /path/to/workdir
```

### Key Flags

- `--print`: Non-interactive print mode (no shell UI)
- `--yolo` / `-y`: Auto-approve all actions (no prompts)
- `-c "command"`: Send command directly
- `-w /path`: Set working directory

### Output Format

Kimi outputs structured text in print mode:
- `StepBegin(n=1)` - Start of execution step
- `TextPart(...)` - LLM responses
- `ToolCall(...)` - Tool being called (e.g., WriteFile)
- `ToolResult(...)` - Result of tool execution
- `StatusUpdate(...)` - Context usage stats

### Example Session

```bash
$ cd /tmp && kimi --print --yolo -c "create a simple hello.py file"
create a simple hello.py file
StepBegin(n=1)
TextPart(type='text', text='I'll create a simple hello.py file...')
ToolCall(type='function', id='WriteFile:0', ...)
ToolResult(tool_call_id='WriteFile:0', result=ToolOk(...))
StepBegin(n=2)
TextPart(type='text', text='File created successfully...')
```

### Implementation Implications

1. **No pexpect needed** - Use `subprocess.run()` or `subprocess.Popen()`
2. **No prompt detection** - Command returns when done
3. **Timeout handling** - Use subprocess timeout parameter
4. **Error detection** - Check return code and stderr
5. **Auth** - Already logged in (user confirmed), no `/setup` flow needed

### Session Class Approach

```python
def send_prompt(self, prompt: str) -> str:
    cmd = [
        "kimi",
        "--print",
        "--yolo",
        "-w", str(self.working_dir),
        "-c", prompt
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=self.timeout)
    return result.stdout.decode()
```

### Auth Check

Since user confirmed Kimi is already logged in, we can skip complex auth flows. If auth is needed in future:
- Run a simple test command
- Check for auth error in output
- Return clear error message

## Conclusion

This is MUCH simpler than the original pexpect-based approach. Implementation will be straightforward using subprocess instead of pexpect.
