---
description: Link the .agent folder to another project so Antigravity uses the same global agents, skills, workflows and scripts.
---

# /link-agent — Global Agent Linker

Links the master `.agent` folder to one or more target projects using NTFS Junction Points.

## Steps

1. **Ask the user** which project(s) to link. Accept:
   - A single project path
   - Multiple paths
   - "all" to link every subdirectory in `C:\Users\Daniel Palma\Documents`

2. **Check if GEMINI.md** should also be linked/copied. Ask the user.

3. **Run the linker script** with the provided paths:

// turbo
```powershell
# Single project example:
& "C:\Users\Daniel Palma\Documents\graficos matematicos\.agent\scripts\link-agent-global.ps1" `
    -TargetProject "<PROJECT_PATH>" `
    -MasterAgent "C:\Users\Daniel Palma\Documents\graficos matematicos"
```

4. **If GEMINI.md was requested**, copy it to each target project:

```powershell
Copy-Item "C:\Users\Daniel Palma\Documents\graficos matematicos\GEMINI.md" -Destination "<PROJECT_PATH>\GEMINI.md" -Force
```

5. **Verify** the junction was created:

// turbo
```powershell
Get-Item "<PROJECT_PATH>\.agent" | Select-Object FullName, Attributes, Target
```

6. **Report results** to the user with a summary table.

## Notes

- Junctions do NOT require admin privileges (unlike symlinks).
- If a `.agent` folder already exists at the target, the script backs it up automatically.
- To remove a junction safely: `Remove-Item "<path>\.agent" -Force` (NEVER use `-Recurse`).
- Master .agent location: `C:\Users\Daniel Palma\Documents\graficos matematicos\.agent`
