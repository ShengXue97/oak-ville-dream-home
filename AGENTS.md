# Project delivery

- After each completed, validated change, commit and push the corresponding commits to `origin/master`, as requested by the user. Report push failures rather than leaving them unmentioned.
- Inspect repository status first and preserve unrelated edits. Never force-push, rewrite history, or create tags/releases without explicit authorization.
- Keep Git LFS enabled for the main Blender deliverable and Unreal binary assets. Ensure the pre-push hook uploads required LFS objects. When auditing missing uploads, scope the audit to objects referenced by the current project files unless broader history is explicitly requested.
- Follow the existing Semantic Versioning and changelog workflow. Documentation-only changes do not need an application version bump.
