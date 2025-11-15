# Test Prompts for Kimi-Coder-MCP

This document contains example prompts for testing all 5 MCP tools with Kimi CLI.

## Prerequisites

1. **Restart Claude Code** after updating MCP configuration
2. Verify Kimi CLI is installed: `kimi --version`
3. Ensure you're logged into Kimi (or have MOONSHOT_API_KEY set)
4. Navigate to a test directory before running prompts

---

## Tool 1: kimi_code_task

**Purpose**: Execute coding tasks with file creation/modification tracking

### Test Prompt 1: Simple File Creation
```
Use the kimi_code_task tool to create a simple Python script that:
1. Defines a function to calculate fibonacci numbers
2. Includes a main block that prints the first 10 fibonacci numbers
3. Save it as fibonacci.py
```

**Expected Result**:
- `success: true`
- `files_created: ["fibonacci.py"]`
- `file_contents` contains the Python code

### Test Prompt 2: Task with Context Files
```
I have a utils.py file in my current directory. Use kimi_code_task to create a new module called math_helpers.py that:
1. Imports functions from utils.py
2. Adds helper functions for basic math operations
3. Uses the context_files parameter to reference utils.py
```

**Expected Result**:
- File created with imports from context
- Context files properly included in prompt

### Test Prompt 3: Multiple File Creation
```
Use kimi_code_task to create a simple web scraper project:
1. scraper.py - main scraping logic
2. config.py - configuration settings
3. requirements.txt - dependencies list
```

**Expected Result**:
- Multiple files in `files_created`
- All file contents returned

---

## Tool 2: kimi_analyze_code

**Purpose**: Analyze code files and provide suggestions (interactive mode)

### Test Prompt 1: Single File Analysis
```
Use kimi_analyze_code to analyze fibonacci.py and provide:
1. Code quality assessment
2. Performance suggestions
3. Best practices recommendations
```

**Expected Result**:
- Detailed analysis in response
- Suggestions array populated
- Interactive mode used (may ask clarifying questions)

### Test Prompt 2: Multiple File Analysis
```
Analyze these files using kimi_analyze_code:
- scraper.py
- config.py
Focus on: architecture and code organization
```

**Expected Result**:
- Analysis covers all files
- Focus area reflected in analysis

### Test Prompt 3: Security-Focused Analysis
```
Use kimi_analyze_code to analyze my authentication.py file.
Focus on: security vulnerabilities and potential exploits
```

**Expected Result**:
- Security-specific suggestions
- Vulnerability identification

---

## Tool 3: kimi_prompt

**Purpose**: Generic prompting with optional workspace context (interactive mode)

### Test Prompt 1: Simple Question
```
Use kimi_prompt to ask Kimi: "What are the best practices for async/await in Python?"
```

**Expected Result**:
- Detailed explanation
- No file changes
- Interactive mode for follow-ups

### Test Prompt 2: With Workspace Context
```
Use kimi_prompt with workspace context enabled to ask:
"Based on the files in this project, what architectural improvements would you suggest?"
```

**Expected Result**:
- Workspace files listed in prompt
- Suggestions based on actual project structure

### Test Prompt 3: Code Generation via Generic Prompt
```
Use kimi_prompt to request:
"Create a simple REST API endpoint for user registration using FastAPI"
```

**Expected Result**:
- File created with API code
- `files_created` contains new file
- Full implementation details

---

## Tool 4: kimi_refactor

**Purpose**: Refactor existing code (one-shot mode)

### Test Prompt 1: Function Refactoring
```
Use kimi_refactor to refactor fibonacci.py:
Instructions: "Extract the fibonacci calculation into a class with caching"
```

**Expected Result**:
- `original_content` shows before state
- `refactored_content` shows after state
- `explanation` describes changes
- `files_modified: ["fibonacci.py"]`

### Test Prompt 2: Code Modernization
```
Refactor my old_style_code.py using kimi_refactor:
Instructions: "Modernize to use Python 3.11+ features including type hints, match statements, and dataclasses"
```

**Expected Result**:
- Before/after comparison
- Detailed explanation of modernizations

### Test Prompt 3: Performance Optimization
```
Use kimi_refactor on slow_algorithm.py:
Instructions: "Optimize for performance - replace O(n²) operations with more efficient algorithms"
```

**Expected Result**:
- Performance improvements documented
- Algorithm changes explained

---

## Tool 5: kimi_debug

**Purpose**: Debug errors interactively with Kimi's help

### Test Prompt 1: Simple Error Debugging
```
Use kimi_debug to help with this error:
Error: "NameError: name 'fibonacci' is not defined"
Relevant files: ["fibonacci.py", "main.py"]
```

**Expected Result**:
- `diagnosis` identifies the issue
- `solution` provides fix
- May modify files to fix the error

### Test Prompt 2: Complex Error with Context
```
Debug this error using kimi_debug:
Error: "RuntimeError: Event loop is closed"
Relevant files: ["async_handler.py", "main.py"]
Context: "This only happens when running the script a second time"
```

**Expected Result**:
- Diagnosis considers the context
- Solution addresses the specific scenario
- Interactive follow-ups possible

### Test Prompt 3: Production Bug
```
Use kimi_debug to investigate:
Error: "Memory leak causing gradual slowdown over 24 hours"
Relevant files: ["worker.py", "queue_handler.py", "database.py"]
Context: "Memory usage grows from 100MB to 2GB over time"
```

**Expected Result**:
- Detailed diagnosis
- Root cause identification
- Suggested fixes

---

## Testing Workflow

### 1. Basic Functionality Test
Run all "Test Prompt 1" examples to verify each tool works

### 2. Integration Test
```
1. Create a project using kimi_code_task
2. Analyze it using kimi_analyze_code
3. Refactor based on suggestions using kimi_refactor
4. Fix any issues using kimi_debug
5. Ask questions using kimi_prompt
```

### 3. Interactive Mode Test
Use tools that support interactive mode (analyze, prompt, debug) and try:
- Asking follow-up questions
- Requesting clarifications
- Having multi-turn conversations

### 4. File Tracking Test
```
1. Take note of current directory state
2. Use kimi_code_task to create files
3. Verify files_created list is accurate
4. Verify file_contents matches actual files
5. Use kimi_refactor and verify files_modified
```

### 5. Error Handling Test
```
1. Try kimi_refactor on a non-existent file
   Expected: FileNotFoundError in response
   
2. Use extremely long timeout task
   Expected: TimeoutError in response
   
3. Test with invalid parameters
   Expected: Proper error messages
```

---

## Expected Behaviors

### Interactive Mode Tools (analyze, prompt, debug)
- May ask clarifying questions
- Support multi-turn conversations
- Can request additional context
- Session persists during interaction

### One-Shot Mode Tools (code_task, refactor)
- Execute single command
- No follow-up questions
- Faster execution
- Deterministic results

### All Tools
- Return structured responses
- Track file changes accurately
- Handle errors gracefully
- Include detailed logging

---

## Troubleshooting

### If Tools Don't Appear in Claude Code
1. Restart Claude Code completely
2. Check MCP config: `cat ~/Library/Application Support/Claude/claude_desktop_config.json`
3. Verify server path is correct
4. Check logs in Claude Code settings

### If Kimi Errors Occur
1. Verify Kimi CLI installed: `kimi --version`
2. Check authentication: `kimi` (should not prompt for setup)
3. Test Kimi directly: `kimi --print --yolo -c "echo test"`

### If File Tracking Fails
1. Check working directory permissions
2. Verify .gitignore patterns aren't too aggressive
3. Check for binary vs text file issues

### If Timeouts Occur
1. Default timeout is 300 seconds (5 minutes)
2. Complex tasks may need longer timeout (future enhancement)
3. Try breaking task into smaller pieces

---

## Performance Benchmarks

### Expected Response Times
- **kimi_code_task**: 5-30 seconds (simple tasks)
- **kimi_analyze_code**: 10-60 seconds (depends on file size)
- **kimi_prompt**: 5-30 seconds (simple queries)
- **kimi_refactor**: 10-45 seconds (depends on file size)
- **kimi_debug**: 15-60 seconds (depends on complexity)

### File Tracking Overhead
- Snapshot creation: <1 second (typical project)
- Change detection: <1 second
- File reading: <1 second for text files

---

## Advanced Test Scenarios

### Scenario 1: Full Development Workflow
```
1. Use kimi_code_task to create a Flask API
2. Use kimi_analyze_code to review the code
3. Use kimi_refactor to apply suggestions
4. Introduce a bug manually
5. Use kimi_debug to find and fix it
6. Use kimi_prompt to ask about deployment
```

### Scenario 2: Large Codebase Analysis
```
1. Create a multi-file project with kimi_code_task
2. Use kimi_analyze_code on all files
3. Track which files need refactoring
4. Use kimi_refactor on each file
5. Verify all changes with file tracking
```

### Scenario 3: Interactive Debugging Session
```
1. Create buggy code with kimi_code_task
2. Use kimi_debug to start investigation
3. Ask follow-up questions in interactive mode
4. Request specific file modifications
5. Verify fixes work
```

---

## Notes

- **Working Directory**: All tools operate in current working directory
- **File Paths**: Use relative paths from working directory
- **Context Files**: Optional for code_task, helps with understanding
- **Interactive vs One-Shot**: Automatically selected based on tool
- **Error Messages**: Always include actionable suggestions

---

**Last Updated**: 2025-01-14
**Version**: 0.1.0
