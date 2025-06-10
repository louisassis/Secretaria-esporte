from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_evento():
    response = client.post(
        "/eventos",
        json={
            "nome": "Evento Teste",
            "data": "2025-06-20",
            "local": "Ginásio de Esportes",
            "tipo": "Basquete",
            "publico_estimado": 200,
            "custo": 1500.50,
            "descricao": "Evento de teste para API",
            "regiao": "Ceilândia"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Evento inserido com sucesso"

def test_listar_eventos():
    response = client.get("/eventos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(ev["nome"] == "Evento Teste" for ev in response.json())
