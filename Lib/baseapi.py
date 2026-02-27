import os
import sys
from abc import ABC

from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

from Lib.configs import DATA_DIR
from Lib.log import logger


class BaseAPI(ABC):

    def __init__(self):
        self.logger = logger

    class _TemplateWrapper:
        """ A template wrapper class hidden internally that does only one thing: provide .format()."""

        def __init__(self, content: str):
            self._content = content

        def format(self, **kwargs) -> str:
            """ Implement the .format() method you want. """
            return self._content.format(**kwargs)

    @staticmethod
    def _get_main_script_name():
        """
        Get the filename of the main execution script (without the extension).
        sys.argv[0] always points to the script that was originally started, regardless of which module the current code is running in.
        """
        try:
            # 1. Get the full path of the main execution script
            script_path = sys.argv[0]

            # 2. Extract the file name from the full path
            script_filename = os.path.basename(script_path)

            # 3. Separate the file name and extension
            script_name, _ = os.path.splitext(script_filename)

            return script_name
        except IndexError as e:
            raise RuntimeError("Unable to get the name of the main execution script, sys.argv[0] does not exist.") from e
        except Exception as e:
            raise RuntimeError(f"An error occurred while getting the name of the main execution script: {e}") from e

    @property
    def module_name(self):
        """Get the module loading path"""
        module_name = self.__module__.split(".")[-1]
        if module_name == "__main__":
            return self._get_main_script_name()
        else:
            return module_name

    def _get_md_file_path(self, filename: str, lang=None) -> str:
        """
        Get the markdown file path based on the workbook name.
        Lookup order:
        1. explicit file path
        2. DATA_DIR/<name>.md (or provided .md)
        3. DATA_DIR/<module_name>/<name>.md (or provided .md)
        """

        if os.path.isfile(filename):  # "/root/asf/ES-Rule-21-Phishing_user_report_mail/senior_phishing_expert.md"
            return filename

        if filename.endswith('.md'):  # "senior_phishing_expert.md"
            fname = filename
        elif lang is not None:
            fname = f"{filename}_{lang}.md"  # "senior_phishing_expert_en.md"
        else:
            fname = f"{filename}.md"  # "senior_phishing_expert.md"

        data_root_path = os.path.join(DATA_DIR, fname)
        if os.path.isfile(data_root_path):
            return data_root_path

        module_scoped_path = os.path.join(DATA_DIR, self.module_name, fname)
        if os.path.isfile(module_scoped_path):
            return module_scoped_path

        raise FileNotFoundError(
            f"Markdown template not found. Checked: {data_root_path} and {module_scoped_path}"
        )

    def _get_file_path(self, filename: str):
        """
        Get the file path based on the workbook name.
        """

        if os.path.isfile(filename):  # "/root/asf/ES-Rule-21-Phishing_user_report_mail/senior_phishing_expert.md"
            return filename

        data_root_path = os.path.join(DATA_DIR, filename)
        if os.path.isfile(data_root_path):
            return data_root_path

        template_path = os.path.join(DATA_DIR, self.module_name, filename)
        if os.path.isfile(template_path):  # "ES-Rule-21-Phishing_user_report_mail/senior_phishing_expert.md"
            return template_path

        raise FileNotFoundError(f"File not exist: {template_path}")

    def load_markdown_template(self, filename: str) -> _TemplateWrapper:
        """
        Read the content according to the workbook name and return an object that supports .format().
        """

        template_path = self._get_md_file_path(filename)
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Return an instance of an inner nested class
                return self._TemplateWrapper(content)

        except Exception as e:
            logger.warning(f"Failed to load prompt template {template_path}: {str(e)}")
            raise

    def load_system_prompt_template(self, filename, lang=None):
        """Load system prompt template"""
        template_path = self._get_md_file_path(filename, lang=lang)
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                system_prompt_template: SystemMessagePromptTemplate = SystemMessagePromptTemplate.from_template(f.read())
                logger.debug(f"Loaded system prompt template from: {template_path}")
                return system_prompt_template
        except Exception as e:
            logger.warning(f"Failed to load prompt template {template_path}: {str(e)}")
            raise

    def load_human_prompt_template(self, filename, lang=None):
        template_path = self._get_md_file_path(filename, lang=lang)
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                human_prompt_template: HumanMessagePromptTemplate = HumanMessagePromptTemplate.from_template(f.read())
                logger.debug(f"Loaded human prompt template from: {template_path}")
                return human_prompt_template
        except Exception as e:
            logger.warning(f"Failed to load prompt template {template_path}: {str(e)}")
            raise

    def run(self):
        raise NotImplementedError
