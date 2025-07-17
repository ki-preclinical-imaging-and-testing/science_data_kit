"""
Utility modules for Science Data Kit.

This package contains various utility modules for the Science Data Kit,
including parallel processing, background processing, and other helper functions.
"""

# Import and expose parallel processing utilities
from science_data_kit.core.utils.parallel_processing import (
    ParallelExecutor,
    ParallelDataProcessor,
    parallel_map,
    parallel_process_dataframe,
    BackgroundTaskManager,
    TaskStatus,
    submit_background_task
)

# Import and expose background processing utilities
from science_data_kit.core.utils.background_processing import (
    run_in_background,
    run_task_in_background,
    get_task_status,
    get_task_result,
    cancel_task,
    get_all_tasks,
    wait_for_task,
    wait_for_tasks,
    shutdown_background_processing,
    get_global_task_manager
)

# Import and expose internationalization utilities
from science_data_kit.core.utils.i18n_utils import (
    translate,
    _,
    get_current_language,
    set_current_language,
    get_available_languages,
    TranslationManager,
    translation_manager
)

__all__ = [
    # Parallel processing
    'ParallelExecutor',
    'ParallelDataProcessor',
    'parallel_map',
    'parallel_process_dataframe',
    'BackgroundTaskManager',
    'TaskStatus',
    'submit_background_task',

    # Background processing
    'run_in_background',
    'run_task_in_background',
    'get_task_status',
    'get_task_result',
    'cancel_task',
    'get_all_tasks',
    'wait_for_task',
    'wait_for_tasks',
    'shutdown_background_processing',
    'get_global_task_manager',

    # Internationalization
    'translate',
    '_',
    'get_current_language',
    'set_current_language',
    'get_available_languages',
    'TranslationManager',
    'translation_manager'
]
