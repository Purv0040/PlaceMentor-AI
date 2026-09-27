import pytest
from app.repositories.github_repository import GitHubRepository


@pytest.mark.asyncio
async def test_github_repository_crud(mock_db):
    repo = GitHubRepository(mock_db)
    user_id = "user_repo_test_1"

    profile = await repo.upsert_github_profile(
        user_id=user_id,
        github_username="testdev",
        profile_info={"login": "testdev", "name": "Test Dev"},
        statistics={"total_repositories": 5, "total_stars": 15}
    )
    assert profile["github_username"] == "testdev"
    profile_id = str(profile["id"])

    found = await repo.find_by_user_id(user_id)
    assert found is not None
    assert found["github_username"] == "testdev"

    repos_list = [
        {"repo_id": 1001, "name": "repo1", "stars": 10, "language": "Python"},
        {"repo_id": 1002, "name": "repo2", "stars": 5, "language": "TypeScript"}
    ]
    upserted_count = await repo.upsert_repositories(user_id, profile_id, repos_list)
    assert upserted_count == 2

    db_repos = await repo.find_repositories_by_user_id(user_id)
    assert len(db_repos) == 2

    await repo.update_sync_status(user_id, "synced", is_success=True)
    synced_prof = await repo.find_by_user_id(user_id)
    assert synced_prof["sync"]["status"] == "synced"

    await repo.save_analysis(user_id, {"summary": "Great portfolio"})
    analyzed_prof = await repo.find_by_user_id(user_id)
    assert analyzed_prof["analysis"]["summary"] == "Great portfolio"

    deleted = await repo.delete_by_user_id(user_id)
    assert deleted is True
    assert await repo.find_by_user_id(user_id) is None
