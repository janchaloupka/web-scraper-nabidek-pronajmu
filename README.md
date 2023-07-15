# Web Scraper Nabídek Pronájmu
Hlídá nové nabídky na populárních realitních serverech.

*Tato aplikace byla vytvořena pro osobní použití, takže obsahuje hardkódované údaje pro hledání pronájmu bytů v Brně (ale nemělo by být zas tak moc těžký to upravit).*

Nicméně je možné při spuštění aplikace nakonfigurovat, které  **dispozice bytu** (počet místností) hledat.

## Podporované realitní servery
- BRAVIS
- EuroBydlení
- iDNES Reality
- REALCITY
- realingo
- Remax
- Sreality
- UlovDomov
- BezRealitky

## Spuštění
- Lze spustit lokálně nebo v Dockeru
- **Lokální spuštění**
    - Je vyžadován **Python 3.11+**
    - Před prvním spuštěním nainstalujte závislosti `make install`
    - Vytvořte si lokální soubor `.env.local` a nastavte v něm všechny požadované parametry (minimálně však Discord token, cílovou roomku a požadované dispozice bytu)
    - následně je možné spustit `make run` nebo v debug režimu `make debug`
- **Spuštění v Dockeru**
    - Přiložená Docker Compose konfigurace souží pro vývoj. Stačí ji spustit příkazem `docker-compose up -d` (má zapnutý debug mód)
    - Kromě toho je možné vytvořit "produkční" Docker image díky `Dockerfile`. Při spuštění kontejneru je nutné nastavit všechny požadované env proměnné (ne v v .env.local!)

Aplikace při prvním spuštění nevypíše žádné nabídky, pouze si stáhne seznam těch aktuálních. Poté každých 30 mint (nastavitelné přes env proměnné) kontroluje nové nabídky na realitních serverech a ty přeposílá do Discord kanálu. Aplikace nemusí běžet pořád, po opětovném spuštění pošle všechny nové nabídky od posledního spuštění.

## Konfigurace přes Env proměnné
- `DISCORD_OFFERS_CHANNEL` - Unikátní číslo Discord kanálu, kde se budou posílat nabídky. [Návod pro získání ID](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)
- `DISCORD_DEV_CHANNEL` - Unikátní číslo Discord kanálu, kde se budou posílat chyby programu.
- `DISCORD_TOKEN` - Obsahuje Discord token bota. [Návod pro získání tokenu](https://discordgsm.com/guide/how-to-get-a-discord-bot-token)
- `DISPOSITIONS` - Obsahuje seznam dispozic oddělených čárkou. Např.: `DISPOSITIONS=2+kk,2+1,others`

### Seznam dostupných hodnot parametru `DISPOSITIONS`
- `1+kk`
- `1+1`
- `2+kk`
- `2+1`
- `3+kk`
- `3+1`
- `4+kk`
- `4+1`
- `5++` (5+kk a více místností)
- `others` (jiné, atypické nebo neznámé velikosti)

### Další konfigurovatelné Env proměnné
Tyto hodnoty jsou nastavené pro bězné použití a není potřeba ji měnit. Zde je každopádně popis těchto hodnot.
- `DEBUG` (boolean, výchozí vypnuto). Aktivuje režim ladění aplikace, především podrobnějšího výpisu do konzole. Vhodné pro vývoj.
- `FOUND_OFFERS_FILE` Cesta k souboru, kam se ukládají dříve nalezené nabídky. Aplikace si soubor vytvoří, ale složka musí existovat. Pokud aplikace nebyla nějakou dobu spuštěna (řádově týdny) je dobré tento soubor smazat - aplikace by toto vyhodnotila jako velké množství nových nabídek a zaspamovala by Discord kanál.
- `REFRESH_INTERVAL_DAYTIME_MINUTES` - interval po který se mají stáhnout nejnovější nabídky Výchozí 30min, doporučeno minimálně 10min
- `REFRESH_INTERVAL_NIGHTTIME_MINUTES` - noční interval stahování nabídek. Jde o čas mezi 22h-6h. Výchozí 90min, doporučeno vyšší než denní interval
