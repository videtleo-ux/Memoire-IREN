"""Pilote d'invocation d'Hermes : le chemin `-z`, prompt lu d'un fichier.

⚠️ Ce fichier n'est **jamais importé par l'arène** : il est exécuté par le
python du venv d'Hermes (`InvocateurHermes` le passe en argument), seul
interpréteur où `hermes_cli` est importable. Aucun test ne doit l'importer.

Pourquoi il existe (audit 2026-08-22, constat C2) : `hermes -z` n'accepte le
prompt que par argv, et CreateProcess plafonne la ligne de commande Windows à
32 767 caractères. Or le prompt ICL de campagne (fenêtre à 3 séries de
K = 150) fait ~51 000 caractères : les 9 runs ICL s'arrêteraient tous en
série 3 (`WinError 206`), après deux séries payées. Réduire K ne répare pas :
tenir 3 séries dans argv exige K ≤ 84, niveau où le critère de stabilité du
PRD 3 §7.3 échoue sur pièces (|écart(80) − écart(200)| = 0,054 > 0,05 sur le
run pilote `medium`).

Ce pilote retire le seul élément qui plafonne — le prompt en argv — sans rien
changer d'autre : `hermes -z` n'est qu'un habillage de
`_run_and_exit_oneshot` (`hermes_cli/main.py`, entry point
`hermes_cli.main:main`), qu'on appelle ici à l'identique — mêmes nettoyages,
mêmes codes retour, même stdout, même `--usage-file`. Vérifié en réel le
2026-08-22 : le prompt ICL série 2 de campagne (34 694 caractères) traverse
ce chemin, réponse exploitable, rapport d'usage `completed: true`.

Usage (toujours les cinq arguments, dans cet ordre) :

    <venv-hermes>/python pilote_oneshot.py <fichier-prompt> <toolset> \
        <modele> <fournisseur> <usage-file>
"""

import sys


def principal() -> None:
    fichier_prompt, toolset, modele, fournisseur, usage = sys.argv[1:6]
    with open(fichier_prompt, encoding="utf-8") as fichier:
        prompt = fichier.read()

    # Le même point d'entrée que l'exécutable `hermes -z` : il appelle
    # `run_oneshot`, exécute le nettoyage global, et sort par `os._exit`.
    from hermes_cli.main import _run_and_exit_oneshot

    _run_and_exit_oneshot(
        prompt,
        model=modele,
        provider=fournisseur,
        toolsets=toolset,
        usage_file=usage,
    )


if __name__ == "__main__":
    principal()
