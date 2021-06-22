import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "http://127.0.0.1:5000"

def test_register(supply_url):
	url = supply_url + "/register" 

	data = {
		"username": "Test account",
		"password": "Test password",
		"repeat_password": "Test password"
	}

	resp = requests.post(url, json=data)
	assert resp.status_code == 200, resp.text
	assert resp.json()['success'] == True, resp.text


	data = {
		"username": "Test account",
		"password": "Test password",
		"repeat_password": "Test password"
	}

	resp = requests.post(url, json=data)
	assert resp.status_code == 200, resp.text
	assert resp.json()['success'] == False, resp.text
	assert resp.json()['errors'][0]['code'] == 'InvalidUsername' ,resp.text


	data = {
		"username": "Test account",
		"password": "Test password",
		"repeat_password": "Test passwords"
	}

	resp = requests.post(url, json=data)
	assert resp.status_code == 200, resp.text
	assert resp.json()['success'] == False, resp.text
	assert resp.json()['errors'][0]['code'] == 'InvalidRepeatPassword' ,resp.text