# D10 — Splitting Economy's Junk wallet from its battle rewards

Date: November 3, 2026. Status: plan for review; no code changed. Resolves SPL-03 (D9 §7) for the
wallet / rewards cut only; the Mod Catalog and Shops extractions follow their own short plans.

Read with D9 (standalone boundaries), D3 §16 (one writer per record), D6 (capability APIs) and the
native port's `mods/host/pe_save.h` (named records, carried when their owner is off).

## 1. The problem

`mods/pe_economy/pe_loot.c` (903 lines) is two features sharing one save record:

- the **wallet**: the Junk counter, Junk items routed into it (bag, storage, Wayne's hand-in,
  steals), spending, the "Junk economy" switch, prices;
- the **rewards**: extra Junk per won battle, the no-hit bonus, rare drops with pity, the cascade
  (economy mods, Super Tool, Mod Permit, Super / Duper Junk, Tools, stat boosters), carried rares.

Both live in one 36-byte record, `"pe_economy.loot"` v1 (`s_st`, guarded by a `_Static_assert`).
A record can't be cut in two without a new layout, and the host refuses two owners of one name.

## 2. Who owns which field today

| Field | Bytes | Belongs to | Notes |
| --- | ---: | --- | --- |
| `junk` | 4 | Wallet | the balance, 0..99999 |
| `steal_bank` | 2 | Wallet | Junk stolen this battle, paid on a win (reset on load) |
| `hits[7]` | 14 | Rewards | per-enemy hits this battle, for the no-hit bonus (reset on load) |
| `rare_dry` | 2 | Rewards | pity progress |
| `rare_carry` | 2 | Rewards | a rare that didn't fit the reward list |
| `rng` | 4 | Rewards | reward RNG (reset on load) |
| `charm_left` | 2 | Rewards | lucky charm battles left |
| `preset` | 1 | **shared** | Relaxed / Normal / Grind: scales income, pity **and prices** |
| `disabled` | 1 | Wallet | "Junk economy" switched off for this game |
| `econ_since`, `permit_since` | 2 | Rewards | guarantees for economy mods and Mod Permits |

The record also carries the old recomp "PELT" upgrade path (versions 1–4), which stays where the
record goes.

## 3. Decision: the Wallet owns the record whole (SPL-03)

- **One writer.** The Wallet registers `"pe_economy.loot"` exactly as today: same name, version 1,
  same 36 bytes, same `check`, `upgrade`, `reset`. Old saves load unchanged.
- **Rewards keeps no copy of the record.** It reads and changes its fields through the Wallet's API
  (§5), so the Wallet is still the only code that the save host reads from or writes to.
- **Rewards off or absent:** its fields stay in the record exactly as loaded and are saved back
  unchanged, so turning Rewards back on resumes the same pity and carried rare. The battle-only
  fields (`hits`, `rng`) are reset on load today and stay that way.
- **Wallet off or absent:** the save host carries the whole record (today's behaviour for any mod
  that is off). Rewards declares `requires = {"pe_economy"}`: no wallet, no rewards.
- **The shared `preset`:** stored by the Wallet (it scales prices, which the Wallet answers through
  `price()`); Rewards reads it to scale income and pity. The F1 "Difficulty" row stays on the
  Economy page, registered by the Wallet, with the same key, so players' choices keep.
- A record split (Wallet's fields and Rewards' fields in two records) is **not** part of this
  plan. If it is ever wanted, it is a new versioned layout with an `upgrade()` from v1, done
  separately.

## 4. Mod identities

| Mod | Id | Display name | Contents |
| --- | --- | --- | --- |
| Wallet | `pe_economy` (unchanged) | "PE Enhancements: economy" (unchanged) | the counter and routing half of `pe_loot.c`, the Junk counter display, the record, the `junk` service, the Difficulty and Junk economy rows; for now also Catalog, Shops and the rest of today's economy until their own splits |
| Rewards | `pe_rewards` (new) | "PE Enhancements: battle rewards" | the rewards half of `pe_loot.c`: battle Junk, no-hit bonus, rares, pity, cascade, carried rares; later the playstyle presets |

Keeping the Wallet as `pe_economy` means its mod id, its Manage-mods row and its record need no
alias. The new Rewards row starts from the Economy row's on / off value (`pe_menu_alias_setting`,
as the Wardrobe did from the Collection). F1 rows keep their page and label, so their saved values
carry over whichever mod registers them.

## 5. The Wallet's API: `junk` v1 stays, `wallet` v1 is added

`junk` v1 (`PeJunkApi`) is unchanged; Catalog, Shops, Wardrobe, Collection and Combine keep using
it. A new service, for Rewards only, gives typed access to its fields without exposing the
record:

```c
/* "wallet" v1: published by pe_economy. Rewards' fields in "pe_economy.loot", copied in and out.
 * get/put never spend, grant or save; the save host saves the record when the game saves. */
typedef struct PeRewardState {
    uint16_t hits[7];
    uint16_t rare_dry, rare_carry;
    uint32_t rng;
    uint16_t charm_left;
    uint8_t econ_since, permit_since;
} PeRewardState;

typedef struct PeWalletApi {
    uint32_t struct_size;                       /* sizeof(PeWalletApi), D6 §3 */
    void (*get_rewards)(PeRewardState *out);
    void (*put_rewards)(const PeRewardState *in);
    int (*preset)(void);                        /* 0 Relaxed, 1 Normal, 2 Grind */
    /* This battle's Junk on the items-found list: the Wallet shows one "Junk xN" entry for all of
     * it (vanilla Junk, steals, and what Rewards adds here before the list is built). */
    void (*battle_junk)(uint32_t n);
} PeWalletApi;
```

Copy in, copy out (rather than a pointer into the record) keeps one writer and lets the Wallet
clamp what it stores.

## 6. Splitting the battle-end hook

Today one handler (`pe_on_rewards`, PE_HOOK_BATTLE_REWARDS) does both jobs. After the split:

1. **Rewards, early priority:** computes `earned` (floor + EXP / divisor, caps, no-hit bonus,
   preset, Scavenger), calls `battle_junk(earned)`, rolls rares (pity, cascade, carry) and appends
   them to the reward list, then `put_rewards`.
2. **Wallet, late priority:** takes vanilla Junk off the list, adds the steal bank and what
   `battle_junk` collected, and shows it as one "Junk xN" entry (or pays it straight in when there
   is no room), exactly as today.

With Rewards off, step 1 doesn't run: vanilla Junk and steals still go into the counter, there is
no extra Junk and no rare drops. That is the "wallet without rewards" combination D9 §3 asks for.

The items-found tick (gold names, "<mod> mod" entries, taking the Junk entry) splits the same way:
the Junk entry stays with the Wallet, the rare and economy-mod entries go with Rewards.

## 7. What stays the same

- `"pe_economy.loot"` v1 bytes, name, owner mod id and upgrade path.
- Every number: income formula, caps, pity, cascade order, guarantees, prices.
- F1 rows, pages and labels; tuning rows move with the code they tune (Rewards' tuning stays on
  Debug > Loot tuning).
- The `junk` service and every current consumer.

## 8. Tests (all must pass before the split ships)

1. **Save compatibility.** Write a 36-byte v1 record with every field set; load it in the split
   build: the Wallet's fields read back, `get_rewards` returns the Rewards fields exactly. A recomp
   "PELT" v4 block still upgrades.
2. **Rewards off.** Load, play a battle, save: the Rewards fields in the saved record are
   byte-identical to the loaded ones; the Junk balance changed only by vanilla Junk and steals.
3. **Parity.** A fixture runs the same N battles (EXP, hits, boss flag, Scavenger, preset, RNG
   seed) through today's `pe_loot.c` and through Wallet + Rewards: identical Junk, identical
   reward lists, identical record bytes after each battle.
4. **Absent builds.** Wallet-only and Wallet + Rewards games build; a Rewards-only build refuses to
   start Rewards (needs `pe_economy`) and carries the record.
5. **Settings.** A player who had turned Economy off starts with Rewards off; Difficulty and
   tuning rows keep their saved values.
6. In game: a save made before the split loads with the same Junk, the next rare arrives when pity
   says, and turning Rewards off and on keeps pity.

## 9. Steps

1. Add `PeRewardState` / `PeWalletApi` and publish `wallet` v1 from today's `pe_loot.c`, with no
   behaviour change (Rewards still inside). Parity fixture written against this build.
2. Move the rewards half into `mods/pe_rewards/`, calling the Wallet only through `wallet` and
   `junk`; split the hook and the tick as §6. Parity and save tests must pass unchanged.
3. Settings alias for the Rewards row; README; D9 SPL-03 marked resolved for this cut.
4. Later and separately: playstyle presets land in Rewards with their own record (D3 policy record),
   not in `"pe_economy.loot"`.

## 10. Decisions for the user

1. **Difficulty owner:** the Wallet stores and shows it (it scales prices too), Rewards reads it.
   *Recommended.* The alternative, splitting it into a price setting and a reward setting, changes
   what players see and is out of scope.
2. **Mod ids:** the Wallet keeps `pe_economy`; Rewards is the new `pe_rewards`. *Recommended:* no
   alias needed for the record or the existing row.
3. **Wallet alone:** vanilla Junk and steals still go into the counter, with no extra Junk and no
   rares. *Recommended.* The alternative is Junk going back into the bag when Rewards is off,
   which is what the existing "Junk economy" switch already does.
