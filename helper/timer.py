"""
Copyright (c) 2023-2025. Vili and contributors.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import time

from helper import printer


def timer(require_input: bool):
    """
    A timer decorator to measure the execution time of a function and optionally
    require user input after execution.

    :param require_input: Boolean flag to determine if input is required after execution
    """

    def decorator(func):
        def wrapper(*args, **kwargs) -> str:
            start_time = time.time()  # Start timing
            result = func(*args, **kwargs)  # Execute the wrapped function
            end_time = time.time()  # End timing

            elapsed_time = end_time - start_time  # Calculate elapsed time
            printer.info(
                f"Completed in {elapsed_time:.4f} seconds."
            )  # Print the elapsed time

            # Prompt the user for input after execution
            if require_input:
                printer.inp("Press Enter key to continue...")  # Prompt for input

            return result  # Return the result of the wrapped function

        return wrapper

    return decorator
