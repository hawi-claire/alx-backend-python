#!/usr/bin/env python3
"""Unit and integration tests for client module"""

import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock, PropertyMock
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient class"""

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test GithubOrgClient.org returns correct value"""
        test_client = GithubOrgClient(org_name)
        test_client.org()
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    @patch('client.GithubOrgClient.org', new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org):
        """Test _public_repos_url returns the correct URL"""
        payload = {"repos_url": "https://api.github.com/orgs/test/repos"}
        mock_org.return_value = payload
        test_client = GithubOrgClient("test")
        self.assertEqual(
            test_client._public_repos_url,
            "https://api.github.com/orgs/test/repos"
        )

    @patch('client.get_json')
    @patch('client.GithubOrgClient._public_repos_url',
           new_callable=PropertyMock)
    def test_public_repos(self, mock_public_repos_url, mock_get_json):
        """Test public_repos returns the correct list of repos"""
        test_payload = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = test_payload
        mock_public_repos_url.return_value = "test_url"
        
        test_client = GithubOrgClient("test")
        result = test_client.public_repos()
        
        self.assertEqual(result, ["repo1", "repo2"])
        mock_public_repos_url.assert_called_once()
        mock_get_json.assert_called_once_with("test_url")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license returns the correct value"""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Set up for the integration tests"""
        # Create patcher for requests.get
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        
        # Define side effect function for mocked get
        def side_effect(url):
            """Returns mocked response based on url"""
            if url == "https://api.github.com/orgs/google":
                mock_response = Mock()
                mock_response.json.return_value = cls.org_payload
                return mock_response
            elif url == cls.org_payload["repos_url"]:
                mock_response = Mock()
                mock_response.json.return_value = cls.repos_payload
                return mock_response
            return None
        
        # Set side effect
        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down for the integration tests"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test for public_repos"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration test for public_repos with license argument"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )
