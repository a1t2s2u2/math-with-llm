FROM leanprover/lean4:latest

RUN lake new mathlib_project
WORKDIR /mathlib_project

RUN echo 'require mathlib from git "https://github.com/leanprover-community/mathlib4"' >> lakefile.lean
RUN lake update
RUN lake build

COPY template.lean /template.lean
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
