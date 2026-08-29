import pytest
import uuid
from pydantic import ValidationError
from common.config.app_config import config
from common.models.messages_af import (
    DataType,
    AgentType as BAgentType,
    StepStatus,
    PlanStatus,
    HumanFeedbackStatus,
    PlanWithSteps,
    Step,
    Plan,
    AgentMessage,
    UserLanguage,
)


def test_enum_values():
    """Test enumeration values for consistency."""
    assert DataType.session == "session"
    assert DataType.plan == "plan"
    assert BAgentType.HUMAN == "Human_Agent"
    assert StepStatus.completed == "completed"
    assert PlanStatus.in_progress == "in_progress"
    assert HumanFeedbackStatus.requested == "requested"


def test_plan_with_steps_update_counts():
    """Test the update_step_counts method in PlanWithSteps."""
    plan_id = str(uuid.uuid4())
    step1 = Step(
        plan_id=plan_id,
        action="Review document",
        agent=BAgentType.HUMAN,
        status=StepStatus.completed,
        session_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
    )
    step2 = Step(
        plan_id=plan_id,
        action="Approve document",
        agent=BAgentType.HR,
        status=StepStatus.failed,
        session_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
    )
    plan = PlanWithSteps(
        plan_id=plan_id,
        steps=[step1, step2],
        session_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        initial_goal="Test plan goal",
    )
    plan.update_step_counts()

    assert plan.total_steps == 2
    assert plan.completed == 1
    assert plan.failed == 1
    assert plan.overall_status == PlanStatus.completed


def test_agent_message_creation():
    """Test creation of an AgentMessage."""
    agent_message = AgentMessage(
        session_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        plan_id=str(uuid.uuid4()),
        content="Test message content",
        source="System",
    )
    assert agent_message.data_type == "agent_message"
    assert agent_message.content == "Test message content"


def test_plan_initialization():
    """Test Plan model initialization."""
    plan = Plan(
        plan_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        initial_goal="Complete document processing",
    )
    assert plan.data_type == "plan"
    assert plan.initial_goal == "Complete document processing"
    assert plan.overall_status == PlanStatus.in_progress


def test_step_defaults():
    """Test default values for Step model."""
    step = Step(
        plan_id=str(uuid.uuid4()),
        action="Prepare report",
        agent=BAgentType.GENERIC,
        session_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
    )
    assert step.status == StepStatus.planned
    assert step.human_approval_status == HumanFeedbackStatus.requested


def test_user_language_valid():
    """Test valid browser language tags."""
    for lang in ["en", "en-US", "fr-FR", "zh_CN", "es-419"]:
        ul = UserLanguage(language=lang)
        assert ul.language == lang


def test_user_language_invalid():
    """Test that invalid language codes raise ValidationError to prevent injection/pollution."""
    invalid_inputs = [
        "a",  # too short
        "a" * 36,  # too long
        "en<script>",  # special characters
        "../../etc/passwd",  # path traversal attempt
        "en US",  # contains spaces
        "en;DROP TABLE users;",  # SQL/command injection attempt
    ]
    for invalid in invalid_inputs:
        with pytest.raises(ValidationError):
            UserLanguage(language=invalid)


def test_app_config_set_user_local_browser_language():
    """Test that set_user_local_browser_language validates input before updating environment."""
    config.set_user_local_browser_language("fr-CA")
    assert config.get_user_local_browser_language() == "fr-CA"

    # Attempt setting an invalid language string; environment variable should not update
    config.set_user_local_browser_language("<malicious_payload>")
    assert config.get_user_local_browser_language() == "fr-CA"
