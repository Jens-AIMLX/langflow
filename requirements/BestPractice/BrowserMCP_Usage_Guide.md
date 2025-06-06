# BrowserMCP Usage Guide

## Understanding Click Operations in BrowserMCP

When using BrowserMCP for automating browser interactions, it's important to understand the potential issues and solutions for reliable element clicking.

### Observations from Testing

#### Successful vs. Failed Click Operations

**Successful clicks typically:**
- Target fully initialized elements
- Work better on navigation elements
- Succeed after the page has been loaded for several seconds
- Work better after user interaction has already happened on the page

**Failed clicks often:**
- Target elements that are visually rendered but not fully initialized
- Happen too quickly after page load
- Target complex interactive components

### Common Error Patterns

1. **WebSocket timeouts**: `Error: WebSocket response timeout after 30000ms` indicates the element was found but the click action didn't complete in time. This is different from a connection issue.

2. **Connection issues**: When BrowserMCP has no connection, the error is explicitly "no connection" rather than a timeout.

3. **Same element, different results**: The same element might fail on first attempt but succeed later, suggesting timing issues with front-end framework initialization.

## Best Practices for BrowserMCP Click Operations

### General Guidelines

1. **Wait for page stabilization**:
   - Add a small wait (3-5 seconds) after navigation before attempting clicks
   - Ensure the page is fully loaded and rendering is complete

2. **Element verification**:
   - Take a fresh snapshot immediately before clicking to ensure you have the correct reference IDs
   - Verify element properties in the snapshot to ensure it's the right target

3. **Progressive interaction**:
   - Start with simpler interactions (hover) before attempting clicks
   - Build up complexity gradually

### Framework-Specific Considerations (React/Vue/Angular)

1. **Component mounting**:
   - SPA frameworks like React render elements before attaching all event handlers
   - Elements in the DOM might not be immediately interactive

2. **Synthetic events**:
   - Modern frameworks use synthetic event systems that might not be ready when the element is visible
   - Allow sufficient time for all event bindings to complete

### Mitigating Failed Clicks

1. **Retry strategy**:
   - If a click fails, wait a few seconds and try again
   - Consider using hover before click to "wake up" the element

2. **Alternative approaches**:
   - For form inputs, try focus actions before typing
   - For navigation, consider direct URL navigation if clicks fail

3. **Debugging techniques**:
   - Check console logs after failed actions
   - Take screenshots to verify UI state

### Critical: Avoiding Restarts

1. **Never restart services independently**:
   - Do not restart the server, client application, or BrowserMCP connection on your own
   - BrowserMCP maintains a synchronized connection state that restarts can break
   - Automatic restarts can lead to process termination and lost connection state

2. **Handling restart scenarios**:
   - If you believe a restart is necessary, always ask the user to perform it
   - Explain why you think a restart is needed
   - Let the user handle reconnecting BrowserMCP afterwards
   - Wait for explicit confirmation that services and connections are ready

3. **When code changes are made**:
   - Even after code changes, prefer to wait for user-initiated restarts
   - Code changes that don't affect routing often don't require restarts
   - For hot module replacement scenarios, ask the user if a refresh is needed

## Differentiating Issues

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| WebSocket timeout | Element found but action blocked | Wait longer, retry, or try simpler action |
| "No connection" error | Connection to BrowserMCP lost | Reconnect to BrowserMCP |
| Element not found | Reference ID changed or element not in DOM | Take fresh snapshot and update reference |
| Action succeeds but no effect | Front-end handler not executing | Check console for JS errors |

## Optimal Click Sequence

For most reliable automation, follow this sequence:
1. Navigate to page
2. Wait 3-5 seconds for page to stabilize
3. Take a fresh snapshot to get current reference IDs
4. Try hover on target element
5. Wait 1-2 seconds
6. Attempt click with current reference ID
7. Verify result with another snapshot

---

## BrowserMCP Click Operation Prompt Template

```
I'd like to click an element on the current page using BrowserMCP. To maximize success:

1. First, take a fresh snapshot of the current page to obtain the latest reference IDs.
2. Wait 3 seconds to ensure the page is stable and all event handlers are attached.
3. If the element is a complex interactive component, try hovering over it first.
4. After locating the element in the snapshot with reference ID {ref_id}, click it using the following parameters:
   - element: "{descriptive_name}"
   - ref: "{ref_id}"
5. After clicking, take another snapshot to verify the action succeeded.
6. If you encounter a "WebSocket response timeout after 30000ms" error:
   - This indicates the element was found but the click action couldn't complete
   - Wait 5 seconds and try again
   - If still unsuccessful, try an alternative approach (navigation, different element)
   - Check console logs for any JavaScript errors
7. If you see a "no connection" error, this indicates a true connection issue rather than an element interaction problem.

IMPORTANT: Never restart the server, client application, or BrowserMCP tools on your own. If you believe a restart is necessary,
explicitly ask the user to perform the restart and reconnect BrowserMCP. Automated restarts can break the WebSocket connection
or kill the BrowserMCP process entirely.

Remember: WebSocket timeouts don't mean the connection is broken; they indicate the action itself timed out.
```

This template should be customized with the specific element name and reference ID for each click operation. 