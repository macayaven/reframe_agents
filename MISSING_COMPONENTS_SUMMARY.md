# Missing Components Summary for E2E Testing

## Executive Summary
The Reframe Agents project has the core structure in place but is missing critical implementation details that prevent it from running end-to-end. The main issues are:

1. **No prompts available** (system crashes on startup)
2. **State management broken** (data doesn't flow between agents)
3. **Tools incomplete** (loops don't terminate properly)

## Critical Missing Components

### 🔴 Priority 1: Showstoppers (App Won't Start)

| Component | Issue | Impact | Fix Required |
|-----------|-------|--------|--------------|
| **Prompts** | Langfuse prompts don't exist | Agents fail to initialize | Add fallback prompts |
| **Parser Prompt** | Not in download list | Parser agent fails | Add to langfuse_cli.py |
| **Environment** | No .env setup guide | Users don't know requirements | Created .env.example |

### 🟡 Priority 2: Functional Issues (App Starts but Doesn't Work)

| Component | Issue | Impact | Fix Required |
|-----------|-------|--------|--------------|
| **State Flow** | intake_data never set | PDF has no content | Fix exit_loop tool |
| **State Flow** | analysis_output never set | PDF missing analysis | Add output mechanism |
| **Parser Input** | Can't read conv_raw | Parser gets no data | Fix prompt reference |
| **Loop Exit** | Collectors run forever | Never progresses | Implement exit logic |

### 🟢 Priority 3: Quality Issues (App Works but Poorly)

| Component | Issue | Impact | Fix Required |
|-----------|-------|--------|--------------|
| **Error Handling** | No fallbacks | Crashes on external failures | Add try/catch blocks |
| **Validation** | No state checks | Silent failures | Add state validation |
| **Web Search** | Tool missing | Limited analysis | Implement web tool |
| **Testing** | No test data | Can't verify fixes | Create fixtures |

## File Structure Analysis

### ✅ What Exists
```
app/
├── agents/          ✅ All agents defined
├── callbacks/       ✅ All callbacks implemented  
├── tools/          ⚠️  Tools exist but incomplete
├── services/       ⚠️  Services exist but need fixes
└── config/         ✅ Configuration complete
```

### ❌ What's Missing
```
app/
├── prompts/        ❌ No fallback prompts
├── tools/
│   └── web_search.py    ❌ Not implemented
│   └── set_output.py    ❌ Needed for state
└── main.py         ❌ No direct entry point
```

## Quick Fix Checklist

To get a minimal working version:

- [ ] Add fallback prompts to langfuse_cli.py
- [ ] Add parser prompt to download list
- [ ] Fix exit_loop to set intake_data
- [ ] Create mechanism for analysis_output
- [ ] Update parser prompt to read ${conv_raw}
- [ ] Add .env with Google API key

## Recommended Implementation Order

### Phase 1: Make It Start (1-2 hours)
1. Add fallback prompts
2. Fix prompt download list
3. Create .env file

### Phase 2: Make It Work (2-4 hours)
1. Fix exit_loop tool
2. Add analysis output mechanism
3. Fix state variable references

### Phase 3: Make It Good (4-8 hours)
1. Add error handling
2. Create test fixtures
3. Implement web search
4. Add integration tests

## Testing Milestones

### Milestone 1: "It Starts"
- `poetry run poe web` doesn't crash
- ADK UI loads in browser
- Agents initialize without errors

### Milestone 2: "It Talks"
- User can have conversation
- Bot responds appropriately
- Conversation ends properly

### Milestone 3: "It Works"
- Parser extracts correct data
- Analysis provides reframing
- PDF generates with content

### Milestone 4: "It's Ready"
- Error scenarios handled
- Tests pass
- Deployable to Cloud Run

## Next Steps

1. **Review** this plan with the team
2. **Prioritize** which fixes to implement first
3. **Assign** tasks to team members
4. **Execute** implementation plan
5. **Test** each milestone

With these fixes implemented, the system should successfully complete an end-to-end cognitive reframing session through the ADK web interface.