# STM32 nRF24L01+ — Communication sans fil TX/RX

**Auteurs :** TURGUT Iprahim · PREVOST Alexian · Mbassi Ewolo Loïc Aron

Communication sans fil entre deux cartes STM32L476RG via le module nRF24L01+.
Un seul fichier `main.c` gère les deux modes : émetteur (TX) et récepteur (RX), sélectionnables à la compilation.

> **Statut : Communication TX → RX opérationnelle et validée.**

---

## Table des matières

- [Compatibilité](#compatibilité)
- [Matériel requis](#matériel-requis)
- [Connexions SPI](#connexions-spi)
- [Configuration du mode](#configuration-du-mode)
- [Principe de fonctionnement](#principe-de-fonctionnement)
- [Configuration SPI](#configuration-spi)
- [Paramètres radio](#paramètres-radio)
- [Communication UART](#communication-uart)
- [Gestion des interruptions](#gestion-des-interruptions)
- [Gestion des erreurs](#gestion-des-erreurs)
- [Prochaine étape](#prochaine-étape)

---

## Compatibilité

| Élément | Valeur |
|--------|--------|
| Carte cible | **STM32L476RG** (Nucleo-L476RG) |
| IDE | **STM32CubeIDE 2.1.0** |
| Autres cartes STM32 | Non compatibles sans reconfiguration |
| Versions IDE antérieures | Peuvent générer des erreurs lors des modifications `.ioc` |

---

## Matériel requis

- 2× carte Nucleo-L476RG
- 2× module nRF24L01+
- 2× ordinateurs avec STM32CubeIDE 2.1.0
- Câbles Dupont pour le câblage

---

## Connexions SPI

Le module nRF24L01+ est connecté au bus **SPI3** du STM32. Le CSN est géré en software.

| nRF24L01+ | Broche STM32 | Description |
|-----------|-------------|-------------|
| VCC | 3.3V | Alimentation |
| GND | GND | Masse |
| CE | PB15 | Chip Enable (activation TX/RX) |
| CSN | PA11 | Chip Select (actif bas, géré en software) |
| SCK | PC10 | Horloge SPI |
| MOSI | PC12 | Données maître → esclave |
| MISO | PC11 | Données esclave → maître |
| IRQ | PA10 | Interruption (falling edge) |

---

## Configuration du mode

Dans `main.c`, décommenter **une seule** des deux lignes suivantes avant de flasher :

```c
#define TRANSMITTER   // ← Mode émetteur
// #define RECEIVER   // ← Mode récepteur
```

Le projet est identique sur les deux machines. Seul ce `#define` diffère.

---

## Principe de fonctionnement

### Mode TRANSMITTER

```
[PC / Python] ──UART──▶ [STM32 TX] ──nRF24──▶ [STM32 RX]
                ◀──────── TX_OK / TX_ECHEC / TIMEOUT
```

1. Le STM32 attend des données via UART (interruption `HAL_UART_RxCpltCallback`)
2. À réception, le payload est transmis via nRF24L01+
3. L'IRQ signale le résultat (succès ou échec)
4. Le statut est renvoyé via UART :

| Réponse UART | Signification |
|-------------|---------------|
| `TX_OK` | Paquet transmis avec succès |
| `TX_ECHEC` | Nombre maximum de retransmissions atteint |
| `TIMEOUT` | Pas de réponse IRQ dans les 100 ms |

5. La LED LD2 clignote à chaque envoi réussi

### Mode RECEIVER

```
[STM32 TX] ──nRF24──▶ [STM32 RX] ──UART──▶ [PC / Terminal]
```

1. Le STM32 attend un paquet radio via IRQ (`HAL_GPIO_EXTI_Callback`)
2. À réception, le payload est lu
3. Les données sont affichées via UART : `Recu: <données>`
4. La LED LD2 toggle à chaque réception

---

## Configuration SPI

Le bus SPI3 est configuré en mode maître :

| Paramètre | Valeur |
|-----------|--------|
| Mode | Maître |
| Direction | Full-duplex (2 lignes) |
| Taille des données | 8 bits |
| CPOL / CPHA | 0 / 0 (mode 0) |
| NSS | Software (`SPI_NSS_SOFT`) |
| Ordre des bits | MSB en premier |
| Prescaler | 128 |

> La broche **CE** (PB15) est contrôlée séparément pour activer les modes émission/réception du nRF24L01+.
> Le **CSN** (PA11) est mis à l'état haut par défaut et piloté manuellement.

---

## Paramètres radio

```c
// Initialisation TX
nrf24l01p_tx_init(2500, _250kbps);

// Initialisation RX
nrf24l01p_rx_init(2500, _250kbps);
```

| Paramètre | Valeur |
|-----------|--------|
| Canal radio | 2500 MHz |
| Débit | 250 kbps |

---

## Communication UART

| Paramètre | Valeur |
|-----------|--------|
| Baudrate | 115200 |
| Format | 8N1 (8 bits, pas de parité, 1 bit stop) |
| Interface | USART2 (via USB ST-Link sur Nucleo) |

> **Note :** En mode TX, ne pas appeler `printf` avant `HAL_UART_Receive_IT()` : la réception IT doit être lancée en premier.

---

## Gestion des interruptions

### UART — `HAL_UART_RxCpltCallback()`

Déclenchée à chaque réception complète d'un payload UART côté TX.
→ Positionne le flag `uart_received = 1`, traité dans la boucle principale.

### IRQ nRF24L01+ — `HAL_GPIO_EXTI_Callback()`

Déclenchée sur front descendant de la broche IRQ (PA10).

| Mode | Flag STATUS | Action |
|------|-------------|--------|
| TX | `TX_DS` (bit 5) | `tx_done = 1` — succès |
| TX | `MAX_RT` (bit 4) | `tx_done = 2` — échec, flush FIFO |
| RX | `RX_DR` | Lecture du payload dans `rx_buf` |

> **Prérequis critique** : le handler `EXTI15_10_IRQHandler` doit être présent dans `stm32l4xx_it.c`.
> Sans lui, **aucune interruption IRQ ne sera traitée** :
>
> ```c
> void EXTI15_10_IRQHandler(void)
> {
>     HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_10);
> }
> ```

---

## Gestion des erreurs

En cas de **TIMEOUT** (pas de réponse IRQ dans les 100 ms) :

```c
uint8_t s = nrf24l01p_get_status();

if (s & 0x10) {
    nrf24l01p_flush_tx_fifo();   // Vider la FIFO TX
    nrf24l01p_clear_max_rt();    // Remettre à zéro le flag MAX_RT
}
if (s & 0x20) {
    nrf24l01p_clear_tx_ds();     // Remettre à zéro le flag TX_DS
}
```

Cette procédure évite que le module reste bloqué et permet une nouvelle tentative d'émission.

---

## Prochaine étape

Mise en place d'une **communication bidirectionnelle** : chaque carte pourra être simultanément émetteur et récepteur, permettant :

- l'envoi de **commandes vers le drone**
- la réception de **données de télémétrie** en retour
