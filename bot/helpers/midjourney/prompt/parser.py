import re
from .prompt import Prompt


class Parser:
    def parse(self, prompt: str) -> Prompt:
        # Normalized
        # Telegram on desktop replace '--' with '—', we should keep that in mind
        normalized_prompt = re.sub(r"—", "--", prompt)
        normalized_prompt = re.sub(r" {2,}", " ", normalized_prompt)
        normalized_prompt = normalized_prompt.strip()
        # Reference images zone
        reference_images_match = re.search(r"^(https?:\/\/\S+\s)*", prompt)
        prompt_without_reference_images = prompt[reference_images_match.end():]

        prompt_reference_images = reference_images_match.group().split()
        # Params zone
        params_matches = re.findall(
            r"--(?P<flag_name>\w+)(?:(?:\s|$)(?:(?P<flag_value>(?:(?!--).)*)(?:\s|$)))?",
            prompt_without_reference_images,
        )

        prompt_without_params = re.sub(
            r"--(?P<flag_name>\w+)(?:(?:\s|$)(?:(?P<flag_value>(?:(?!--).)*)(?:\s|$)))?",
            "",
            prompt_without_reference_images,
        )

        prompt_params = dict(params_matches)
        # Text zone
        prompt_text = prompt_without_params.strip()

        # Params additional
        if "sref" in prompt_params:
            prompt_params["sref"] = prompt_params["sref"].replace(
                ",", "").split()
        if "cref" in prompt_params:
            prompt_params["cref"] = prompt_params["cref"].replace(
                ",", "").split()

        return Prompt(prompt_reference_images, prompt_text, prompt_params)
