"""Tests for creators DB models - field assignment."""

import uuid
from datetime import UTC, datetime

from backend.db.models.creators import (
    ContentAuthorization,
    CreatorCampaign,
    CreatorInvitation,
    CreatorProfile,
)


class TestCreatorProfile:
    def test_fields(self) -> None:
        ws_id = uuid.uuid4()

        profile = CreatorProfile()
        profile.workspace_id = ws_id
        profile.platform_creator_id = "tiktok_12345"
        profile.username = "coolcreator"
        profile.display_name = "Cool Creator"
        profile.avatar_url = "https://cdn.tiktok.com/avatar.jpg"
        profile.bio = "Making cool videos"
        profile.follower_count = 150000
        profile.following_count = 500
        profile.likes_count = 3000000
        profile.video_count = 200
        profile.tier = "MACRO"
        profile.categories = ["fashion", "lifestyle"]
        profile.audience_demographics = {
            "age": {"18-24": 0.4, "25-34": 0.35},
            "gender": {"male": 0.45, "female": 0.55},
        }
        profile.engagement_rate = "5.2"
        profile.is_saved = True
        profile.detail_json = {"raw": "snapshot"}

        assert profile.workspace_id == ws_id
        assert profile.platform_creator_id == "tiktok_12345"
        assert profile.username == "coolcreator"
        assert profile.display_name == "Cool Creator"
        assert profile.avatar_url == "https://cdn.tiktok.com/avatar.jpg"
        assert profile.bio == "Making cool videos"
        assert profile.follower_count == 150000
        assert profile.following_count == 500
        assert profile.likes_count == 3000000
        assert profile.video_count == 200
        assert profile.tier == "MACRO"
        assert profile.categories == ["fashion", "lifestyle"]
        assert profile.audience_demographics["gender"]["female"] == 0.55
        assert profile.engagement_rate == "5.2"
        assert profile.is_saved is True
        assert profile.detail_json == {"raw": "snapshot"}


class TestCreatorCampaign:
    def test_fields(self) -> None:
        ws_id = uuid.uuid4()
        start = datetime(2026, 3, 1, tzinfo=UTC)
        end = datetime(2026, 3, 31, tzinfo=UTC)

        campaign = CreatorCampaign()
        campaign.workspace_id = ws_id
        campaign.name = "Spring Launch"
        campaign.description = "Spring product launch collaboration"
        campaign.status = "ACTIVE"
        campaign.budget = "10000.00"
        campaign.start_date = start
        campaign.end_date = end
        campaign.target_categories = ["beauty", "skincare"]
        campaign.requirements = {"min_followers": 10000, "min_engagement": 3.0}

        assert campaign.workspace_id == ws_id
        assert campaign.name == "Spring Launch"
        assert campaign.description == "Spring product launch collaboration"
        assert campaign.status == "ACTIVE"
        assert campaign.budget == "10000.00"
        assert campaign.start_date == start
        assert campaign.end_date == end
        assert campaign.target_categories == ["beauty", "skincare"]
        assert campaign.requirements["min_followers"] == 10000


class TestCreatorInvitation:
    def test_fields(self) -> None:
        campaign_id = uuid.uuid4()
        creator_id = uuid.uuid4()
        responded = datetime(2026, 2, 15, 10, 30, tzinfo=UTC)

        invite = CreatorInvitation()
        invite.campaign_id = campaign_id
        invite.creator_id = creator_id
        invite.status = "ACCEPTED"
        invite.message = "We would love to collaborate with you!"
        invite.offered_amount = "2500.00"
        invite.responded_at = responded

        assert invite.campaign_id == campaign_id
        assert invite.creator_id == creator_id
        assert invite.status == "ACCEPTED"
        assert invite.message == "We would love to collaborate with you!"
        assert invite.offered_amount == "2500.00"
        assert invite.responded_at == responded

    def test_pending_invitation(self) -> None:
        invite = CreatorInvitation()
        invite.campaign_id = uuid.uuid4()
        invite.creator_id = uuid.uuid4()
        invite.status = "PENDING"
        invite.offered_amount = "1000.00"

        assert invite.status == "PENDING"
        assert invite.responded_at is None


class TestContentAuthorization:
    def test_fields(self) -> None:
        ws_id = uuid.uuid4()
        creator_id = uuid.uuid4()
        expires = datetime(2026, 6, 1, tzinfo=UTC)

        auth = ContentAuthorization()
        auth.workspace_id = ws_id
        auth.creator_id = creator_id
        auth.platform_video_id = "video_abc_123"
        auth.authorization_code = "spark_auth_code_xyz"
        auth.status = "APPROVED"
        auth.expires_at = expires

        assert auth.workspace_id == ws_id
        assert auth.creator_id == creator_id
        assert auth.platform_video_id == "video_abc_123"
        assert auth.authorization_code == "spark_auth_code_xyz"
        assert auth.status == "APPROVED"
        assert auth.expires_at == expires

    def test_pending_authorization(self) -> None:
        auth = ContentAuthorization()
        auth.workspace_id = uuid.uuid4()
        auth.creator_id = uuid.uuid4()
        auth.status = "PENDING"

        assert auth.status == "PENDING"
        assert auth.authorization_code is None
        assert auth.platform_video_id is None
        assert auth.expires_at is None
