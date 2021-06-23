include $(shell [ ! -f .mkdkr ] && curl -fsSL https://git.io/JOBYz > .mkdkr; bash .mkdkr init)

lint.shellcheck:
	@$(dkr)
	instance: koalaman/shellcheck-alpine:v0.7.1
	run: shellcheck --exclude=SC2086 src/snippets/pci-group-switcher.sh

lint.flake8:
	@$(dkr)
	instance: python
	run: pip install flake8==3.9.0
	run: flake8 .

.pre-commit: 
	make --silent .git.autopep8

.pos-commit: lint.commit

.git.autopep8:
	for i in $$(git diff --cached --name-only | grep \.py$$); do \
		autopep8 -i $$i; \
		git add $$i; \
	done

.git.hooks:
	$(MAKE) .git/hooks/pre-commit
	$(MAKE) .git/hooks/commit-msg

.git/hooks/pre-commit:
	echo "make .pre-commit" > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

.git/hooks/commit-msg:
	echo "make .pos-commit" > .git/hooks/commit-msg
	chmod +x .git/hooks/commit-msg
