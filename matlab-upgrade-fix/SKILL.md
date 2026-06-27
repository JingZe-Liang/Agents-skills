---
name: fix-ecucoder-s32ds-r2023a-build
description: Diagnose and repair ECUCoder for S32K311/S32K3 projects that simulate in MATLAB/Simulink but fail to compile through ECUCoder and NXP S32 Design Studio after upgrading from MATLAB R2019b to R2023a. Use for Ctrl+B/slbuild failures involving missing MAP files, Eclipsec errors, S32DS workspace launcher prompts, stale Eclipse workspace metadata, hardcoded S32K344DEMO2 paths, Debug_FLASH/sources.mk resource conflicts, or ECUCoder switching from automatic to manual compile.
---

# Fix ECUCoder/S32DS R2023a Build

## What This Fixes

Use this skill when a model still simulates in R2023a but Ctrl+B or `slbuild` fails during ECUCoder post-code-generation, especially with messages like:

- `An error has occurred. See the log file ...\.metadata\.log`
- `无法找到正确的MAP文件`
- `请在S32DS软件中手动完成编译后选择编译完成按钮`
- `Resource ... Debug_FLASH/sources.mk ... already exists` or `does not exist`
- Eclipse/CDT `NullPointerException` in `Builder.getDefaultBuildPath`

Treat this as an integration repair between MATLAB R2023a, ECUCoder, and S32DS. Do not change algorithmic Simulink logic unless normal model compilation still fails before ECUCoder post-processing.

## Known Good Shape

The repaired setup should have:

- ECUCoder config third line set to `1` for automatic S32DS build.
- S32DS workspace prompt disabled: `SHOW_WORKSPACE_SELECTION_DIALOG=false`.
- `.cproject` build path and refresh scope using the actual project name, not stale template names like `S32K344DEMO2`.
- No simultaneously running S32DS GUI/headless build processes during headless `-import`/`-build`.
- Successful S32DS headless build output: `Build Finished. 0 errors`.
- Fresh `Debug_FLASH\<model>.elf`, `<model>.map`, and `<model>.srec`.

## Fast Workflow

1. Identify the model and S32DS project paths.
   - Model example: `E:\2025年车\VCU\E55_1030.slx`
   - Workspace example: `C:\Users\Bobbby\workspaceS32DS.3.5`
   - Project example: `C:\Users\Bobbby\workspaceS32DS.3.5\E55_1030`
   - S32DS example: `D:\NXP\S32DS.3.5`
   - ECUCoder example: `D:\Program Files (x86)\ECUCoder for S32K311`

2. Run the bundled diagnostic script in dry-run mode:

   ```powershell
   .\scripts\diagnose-ecucoder-s32ds.ps1 `
     -ModelName E55_1030 `
     -WorkspacePath 'C:\Users\Bobbby\workspaceS32DS.3.5' `
     -S32DSRoot 'D:\NXP\S32DS.3.5' `
     -ECUCoderRoot 'D:\Program Files (x86)\ECUCoder for S32K311'
   ```

3. If the script reports safe fixes, rerun with `-Fix`:

   ```powershell
   .\scripts\diagnose-ecucoder-s32ds.ps1 `
     -ModelName E55_1030 `
     -WorkspacePath 'C:\Users\Bobbby\workspaceS32DS.3.5' `
     -S32DSRoot 'D:\NXP\S32DS.3.5' `
     -ECUCoderRoot 'D:\Program Files (x86)\ECUCoder for S32K311' `
     -Fix
   ```

4. Close any S32DS GUI or launcher windows before headless verification.

5. Verify import then build:

   ```powershell
   & 'D:\NXP\S32DS.3.5\eclipse\eclipsec.exe' -consoleLog -nosplash `
     -application org.eclipse.cdt.managedbuilder.core.headlessbuild `
     -data 'C:\Users\Bobbby\workspaceS32DS.3.5' `
     -import 'C:\Users\Bobbby\workspaceS32DS.3.5\E55_1030'

   & 'D:\NXP\S32DS.3.5\eclipse\eclipsec.exe' -consoleLog -nosplash `
     -application org.eclipse.cdt.managedbuilder.core.headlessbuild `
     -data 'C:\Users\Bobbby\workspaceS32DS.3.5' `
     -build E55_1030
   ```

6. Return to MATLAB and run either `slbuild('<model>')` or Ctrl+B.

## Manual Repair Details

### ECUCoder Automatic Build Config

Check:

```powershell
Get-Content 'D:\Program Files (x86)\ECUCoder for S32K311\ec311\s32k311_s32dsconfig.txt'
```

Expected first three lines:

```text
D:\NXP\S32DS.3.5
C:\Users\Bobbby\workspaceS32DS.3.5
1
```

Line 3 must be `1`. If it is `0` or missing, ECUCoder will switch to manual compile and may ask the user to click `编译完成`.

### S32DS Workspace Launcher

Edit:

```text
D:\NXP\S32DS.3.5\eclipse\configuration\.settings\org.eclipse.ui.ide.prefs
```

Set:

```text
SHOW_WORKSPACE_SELECTION_DIALOG=false
RECENT_WORKSPACES=C\:\\Users\\Bobbby\\workspaceS32DS.3.5
```

This prevents the S32DS launcher from blocking Ctrl+B. If a launcher is already open after a build has produced ELF/MAP/SREC, close it with `Cancel`.

### S32DS `.cproject`

Inspect both the generated project and ECUCoder template:

```text
<workspace>\<model>\.cproject
<ECUCoderRoot>\S32DSU34\.cproject
```

For a model named `E55_1030`, the key entries should look like:

```xml
<builder buildPath="${workspace_loc:/E55_1030}/Debug_FLASH" ... />
<resource resourceType="PROJECT" workspacePath="/E55_1030"/>
<project id="E55_1030.com.nxp.s32ds.cle.arm.mbs.arm32.bare.gnu.10.2.exe.484677917" ... />
```

Replace stale template names such as `S32K344DEMO2` with the actual model/project name. Do not use `${ProjName}` in `buildPath` if ECUCoder copies it literally and S32DS fails to resolve it.

### Eclipse Workspace Cache

If `.metadata\.log` shows `Builder.getDefaultBuildPath` or `sources.mk` resource conflicts:

1. Close S32DS GUI and make sure no `s32ds.exe`, `eclipsec.exe`, `java.exe`, or `javaw.exe` remains.
2. Run a separate headless `-import` command.
3. Run a separate headless `-build <model>` command.
4. Check `Debug_FLASH` for fresh `.elf`, `.map`, and `.srec`.

Avoid running headless import/build while the S32DS GUI is open on the same workspace.

## MATLAB Verification

In MATLAB, confirm the model still uses ECUCoder's normal post command:

```matlab
bd = 'E55_1030';
get_param(bd, 'PostCodeGenCommand')
get_param(bd, 'SystemTargetFile')
get_param(bd, 'Dirty')
```

Expected:

```text
ec311_pst_s2(buildInfo)
ec311.tlc
off
```

Then build:

```matlab
slbuild('E55_1030')
```

A successful repair ends with MATLAB reporting successful Real-Time Workshop build and S32DS reporting `Build Finished. 0 errors`.

## Warnings That Can Be Non-Blocking

Do not chase these first if ELF/MAP/SREC are produced:

- `Managed Build system manifest file error ... ghs.managedmake...`
- linker warnings about variable-size enums
- Simulink bus element name mismatch warnings
- Stateflow unused data warnings

Only address them after the ECUCoder/S32DS build path is stable.
