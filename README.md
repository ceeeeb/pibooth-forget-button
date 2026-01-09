# pibooth-forget-button

Plugin pour [pibooth](https://github.com/pibooth/pibooth) ajoutant un troisième bouton pour "oublier" les photos.

## Fonctionnalités

- Bouton GPIO dédié pour déplacer les photos vers un dossier "forget"
- LED indicatrice qui clignote pendant l'état d'impression
- Affiche "Photo oubliée !" à l'écran quand une photo est oubliée
- Fonctionne pendant l'état d'impression et l'état d'attente

## Installation

```bash
pip install pibooth-forget-button
```

## Configuration

Dans le fichier `~/.config/pibooth/pibooth.cfg`, ajoutez :

```ini
[FORGET_BUTTON]
# Pin GPIO IN pour le bouton (numérotation BOARD, 0 pour désactiver)
forget_btn_pin = 36

# Pin GPIO OUT pour la LED (0 pour désactiver)
forget_led_pin = 37

# Durée de pression du bouton en secondes
debounce_delay = 0.3
```

## Utilisation

1. Prenez une photo avec pibooth
2. Pendant l'écran d'impression (quand la LED clignote), appuyez sur le bouton forget
3. La photo sera déplacée vers le sous-dossier `forget/` et le message "Photo oubliée !" s'affichera

## Licence

MIT
