include $(shell [ ! -f .mkdkr ] && curl -fsSL https://git.io/JOBYz > .mkdkr; bash .mkdkr init)

lint.shellcheck:
	@$(dkr)
	instance: koalaman/shellcheck-alpine:v0.7.1
	run: shellcheck --exclude=SC2086 snippets/pci-group-switcher.sh

lint.flake8:
	@$(dkr)
	instance: python:3.8-slim
	run: pip install flake8==3.9.0
	run: pip install -r requirements.txt
	run: flake8 .

lint.black:
	@$(dkr)
	instance: python:3.8-slim
	run: pip install black==22.3.0
	run: black --check .

test.unit: test.unit_3_8 test.unit_3_9 test.unit_3_10

test.unit_3_8:
	@$(dkr)
	instance: python:3.8-slim
	run: pip install -r requirements.txt
	run: pip install -r requirements.dev.txt
	run: nose2 -v --with-coverage --coverage-report term

test.unit_3_9:
	@$(dkr)
	instance: python:3.9-slim
	run: pip install -r requirements.txt
	run: pip install -r requirements.dev.txt
	run: nose2 -v --with-coverage --coverage-report term

test.unit_3_10:
	@$(dkr)
	instance: python:3.10-slim
	run: pip install -r requirements.txt
	run: pip install -r requirements.dev.txt
	run: nose2 -v --with-coverage --coverage-report term

dist.publish:
	@$(dkr)
	instance: python:3.8-slim \
		-e TWINE_USERNAME \
		-e TWINE_PASSWORD \
		-e MKDKR_BRANCH_NAME
	run: pip install setuptools wheel twine
	run: pip install -r requirements.txt
	run: sed -i 's/__REPLACE_VERSION__/$$MKDKR_BRANCH_NAME/g' proxmox_pci_switcher/proxmox_pci_switcher.py
	run: rm -rf *.egg-info build dist
	run: python setup.py sdist bdist_wheel
	run: twine upload dist/*

.dist.install:
	rm -rf *.egg-info build dist
	python setup.py sdist bdist_wheel
	python setup.py install -f

.pre-commit: 
	make --silent _dev_black
	make --silent _dev_flake8
	make --silent lint.shellcheck

.pos-commit: lint.commit

_dev_black:
	for i in $$(git diff --cached --name-only | grep \.py$$); do \
		black $$i; \
		git add $$i; \
	done

_dev_flake8:
	flake8 .

.git.hooks:
	$(MAKE) .git/hooks/pre-commit
	$(MAKE) .git/hooks/commit-msg

.git/hooks/pre-commit:
	echo "make .pre-commit" > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

.git/hooks/commit-msg:
	echo "make .pos-commit" > .git/hooks/commit-msg
	chmod +x .git/hooks/commit-msg
