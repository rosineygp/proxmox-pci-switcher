include $(shell [ ! -f .mkdkr ] && curl -fsSL https://git.io/JOBYz > .mkdkr; bash .mkdkr init)

lint.shellcheck:
	@$(dkr)
	instance: koalaman/shellcheck-alpine:v0.7.1
	run: find . -iname *.sh | xargs shellcheck --exclude=SC2086

lint.flake8:
	@$(dkr)
	instance: python:3.8-slim
	run: pip install flake8==3.9.0
	run: pip install -r requirements.txt
	run: flake8 .

lint.black:
	@$(dkr)
	instance: python:3.8-slim
	run: pip install black==20.8b1
	run: black --check .

.pre-commit: 
	make --silent .git.black
	make lint.shellcheck

.pos-commit: lint.commit

.git.black:
	for i in $$(git diff --cached --name-only | grep \.py$$); do \
		black $$i; \
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
