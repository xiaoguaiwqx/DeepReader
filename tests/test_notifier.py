import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from deep_reader.notifier.email_service import EmailNotifier
from deep_reader.models import Paper

@pytest.fixture
def sample_papers():
    return [
        Paper(
            arxiv_id="2301.00001",
            title="Test Paper",
            authors=["Author One"],
            summary="Summary",
            published_date=datetime.now(timezone.utc),
            updated_date=datetime.now(timezone.utc),
            primary_category="cs.AI",
            categories=["cs.AI"],
            pdf_url="http://example.com/pdf"
        )
    ]

@patch("smtplib.SMTP")
@patch.dict("os.environ", {
    "SMTP_USER": "test@example.com",
    "SMTP_PASSWORD": "password",
    "RECIPIENT_EMAIL": "user@example.com"
})
def test_send_daily_digest(mock_smtp, sample_papers):
    # Setup mock
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    notifier = EmailNotifier()
    notifier.send_daily_digest(sample_papers)
    
    # Verify
    mock_smtp.assert_called_once()
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("test@example.com", "password")
    mock_server.send_message.assert_called_once()
    
    # Inspect the message
    args, _ = mock_server.send_message.call_args
    msg = args[0]
    assert msg["To"] == "user@example.com"
    assert "DeepReader Daily Digest" in msg["Subject"]

def test_send_no_papers():
    notifier = EmailNotifier()
    # Should not crash and not send email
    with patch("smtplib.SMTP") as mock_smtp:
        notifier.send_daily_digest([])
        mock_smtp.assert_not_called()
