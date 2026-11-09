import importlib.util
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Carrega a camada de ferramentas sem inicializar o ADK ou usar rede.
arquivo = Path(__file__).parents[1] / "organizador" / "tarefas.py"
spec = importlib.util.spec_from_file_location("tarefas", arquivo)
tarefas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tarefas)


class FerramentasTest(unittest.TestCase):
    def setUp(self):
        self.a_fazer = Mock()
        self.fazendo = Mock()
        self.concluido = Mock()
        for lista, nome, ident in [
            (self.a_fazer, "A fazer", "l1"),
            (self.fazendo, "Em andamento", "l2"),
            (self.concluido, "Concluído", "l3"),
        ]:
            lista.name, lista.id = nome, ident
            lista.list_cards.return_value = []

        self.card = Mock()
        self.card.id, self.card.name = "c1", "Revisar projeto"
        self.a_fazer.add_card.return_value = self.card
        self.a_fazer.list_cards.return_value = [self.card]
        self.board = Mock()
        self.board.open_lists.return_value = [self.a_fazer, self.fazendo, self.concluido]
        patcher = patch.object(tarefas, "_quadro", return_value=self.board)
        self.addCleanup(patcher.stop)
        self.quadro = patcher.start()

    def test_cria_com_data_local_sem_deslocar_dia(self):
        resultado = tarefas.criar_tarefa("Revisar projeto", "Conferir os testes", "2026-11-09")
        self.assertTrue(resultado["ok"])
        self.a_fazer.add_card.assert_called_once_with(
            "Revisar projeto", desc="Conferir os testes", due="2026-11-09T15:00:00+00:00"
        )

    def test_lista_com_status_normalizado(self):
        self.assertEqual(tarefas.listar_tarefas()["cards"][0]["id"], "c1")
        self.assertEqual(tarefas.listar_tarefas("  EM ANDAMENTO ")["cards"], [])

    def test_move_id_do_quadro_para_destino_com_acento(self):
        resultado = tarefas.mover_tarefa("c1", "concluído")
        self.assertEqual(resultado["card"]["status"], "Concluído")
        self.card.change_list.assert_called_once_with("l3")

    def test_recusa_data_e_card_invalido(self):
        self.assertFalse(tarefas.criar_tarefa("A", "B", "2026-02-31")["ok"])
        self.assertFalse(tarefas.mover_tarefa("outro-quadro", "feito")["ok"])
        self.a_fazer.add_card.assert_not_called()
        self.card.change_list.assert_not_called()

    def test_resposta_de_erro_nao_expoe_detalhes(self):
        self.quadro.side_effect = RuntimeError("token-privado")
        resultado = tarefas.listar_tarefas()
        self.assertFalse(resultado["ok"])
        self.assertNotIn("token-privado", resultado["erro"])


if __name__ == "__main__":
    unittest.main()
