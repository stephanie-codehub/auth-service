from typing import Annotated

from pydantic import BeforeValidator

CleanStr = Annotated[str, BeforeValidator(lambda v: str(v).strip() if v else v)]
