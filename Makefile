verify_no_git_changes:
	git diff --quiet || (echo "There are uncommitted changes" && exit 1)	

make clean_branch_for_github:
	rm -rf gitlab-templates
	rm -rf deployment

github_branch: verify_no_git_changes
	git branch -D github 2>/dev/null || true
	git checkout -b github

push_to_github: github_branch
	git push github github:main