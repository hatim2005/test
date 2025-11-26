"""Tests for database models."""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from models.user import User
from models.image import Image, ImageMetadata
from models.job import Job, JobStatus


@pytest.fixture(scope="module")
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    engine.dispose()


class TestUserModel:
    """Test cases for User model."""

    def test_create_user(self, test_db):
        """Test creating a new user."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_pass_123",
            is_active=True,
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.created_at is not None

    def test_user_timestamps(self, test_db):
        """Test that user timestamps are automatically set."""
        user = User(
            email="timestamp@example.com",
            username="timestamp_user",
            hashed_password="hashed_pass_123",
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.created_at <= user.updated_at

    def test_user_uniqueness(self, test_db):
        """Test email uniqueness constraint."""
        user1 = User(
            email="unique@example.com",
            username="user1",
            hashed_password="pass1",
        )
        test_db.add(user1)
        test_db.commit()

        user2 = User(
            email="unique@example.com",
            username="user2",
            hashed_password="pass2",
        )
        test_db.add(user2)

        with pytest.raises(Exception):
            test_db.commit()
        test_db.rollback()


class TestImageModel:
    """Test cases for Image and ImageMetadata models."""

    def setup_method(self):
        """Setup test user for image tests."""
        self.user = User(
            email="image_user@example.com",
            username="image_user",
            hashed_password="pass",
        )

    def test_create_image(self, test_db):
        """Test creating an image."""
        test_db.add(self.user)
        test_db.commit()
        test_db.refresh(self.user)

        image = Image(
            filename="test.jpg",
            file_path="/uploads/test.jpg",
            file_size=102400,
            mime_type="image/jpeg",
            user_id=self.user.id,
        )
        test_db.add(image)
        test_db.commit()
        test_db.refresh(image)

        assert image.filename == "test.jpg"
        assert image.file_size == 102400
        assert image.user_id == self.user.id

    def test_image_metadata(self, test_db):
        """Test image metadata relationships."""
        test_db.add(self.user)
        test_db.commit()
        test_db.refresh(self.user)

        image = Image(
            filename="meta_test.jpg",
            file_path="/uploads/meta_test.jpg",
            file_size=204800,
            mime_type="image/jpeg",
            user_id=self.user.id,
        )
        test_db.add(image)
        test_db.commit()
        test_db.refresh(image)

        metadata = ImageMetadata(
            image_id=image.id,
            width=1920,
            height=1080,
            color_space="RGB",
            format="JPEG",
        )
        test_db.add(metadata)
        test_db.commit()
        test_db.refresh(metadata)

        assert metadata.width == 1920
        assert metadata.height == 1080


class TestJobModel:
    """Test cases for Job model."""

    def test_create_job(self, test_db):
        """Test creating a job."""
        job = Job(
            job_type="color_correction",
            status=JobStatus.PENDING,
            input_data={"image_path": "/path/to/image.jpg"},
        )
        test_db.add(job)
        test_db.commit()
        test_db.refresh(job)

        assert job.job_type == "color_correction"
        assert job.status == JobStatus.PENDING
        assert job.created_at is not None

    def test_job_status_enum(self, test_db):
        """Test job status enum values."""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.PROCESSING.value == "processing"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"

    def test_job_result_update(self, test_db):
        """Test updating job result."""
        job = Job(
            job_type="detection",
            status=JobStatus.PENDING,
            input_data={},
        )
        test_db.add(job)
        test_db.commit()
        test_db.refresh(job)

        job.status = JobStatus.COMPLETED
        job.result_data = {"markers": [[10, 20], [30, 40]]}
        test_db.commit()
        test_db.refresh(job)

        assert job.status == JobStatus.COMPLETED
        assert "markers" in job.result_data
