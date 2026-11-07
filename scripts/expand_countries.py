import json

# Comprehensive list of countries: (Name, Code, [Aliases])
ADDITIONAL_COUNTRIES = [
    ("Afghanistan", "AF", ["Kabul"]),
    ("Albania", "AL", ["Tirana"]),
    ("Algeria", "DZ", ["Algiers"]),
    ("Andorra", "AD", []),
    ("Angola", "AO", ["Luanda"]),
    ("Antigua and Barbuda", "AG", []),
    ("Armenia", "AM", ["Yerevan"]),
    ("Azerbaijan", "AZ", ["Baku"]),
    ("Bahamas", "BS", ["Nassau"]),
    ("Bahrain", "BH", ["Manama"]),
    ("Bangladesh", "BD", ["Dhaka"]),
    ("Barbados", "BB", ["Bridgetown"]),
    ("Belarus", "BY", ["Minsk"]),
    ("Belize", "BZ", []),
    ("Benin", "BJ", []),
    ("Bhutan", "BT", ["Thimphu"]),
    ("Bolivia", "BO", ["La Paz", "Sucre"]),
    ("Bosnia and Herzegovina", "BA", ["Bosnia", "Sarajevo"]),
    ("Botswana", "BW", ["Gaborone"]),
    ("Brunei", "BN", []),
    ("Bulgaria", "BG", ["Sofia"]),
    ("Burkina Faso", "BF", []),
    ("Burundi", "BI", []),
    ("Cabo Verde", "CV", ["Cape Verde"]),
    ("Cambodia", "KH", ["Phnom Penh"]),
    ("Cameroon", "CM", ["Yaounde"]),
    ("Central African Republic", "CF", []),
    ("Chad", "TD", []),
    ("Chile", "CL", ["Santiago"]),
    ("Colombia", "CO", ["Bogota", "Medellin"]),
    ("Comoros", "KM", []),
    ("Congo", "CG", ["Brazzaville"]),
    ("DR Congo", "CD", ["Democratic Republic of the Congo", "Kinshasa"]),
    ("Costa Rica", "CR", ["San Jose"]),
    ("Cote d'Ivoire", "CI", ["Ivory Coast", "Abidjan"]),
    ("Croatia", "HR", ["Zagreb", "Dubrovnik"]),
    ("Cuba", "CU", ["Havana"]),
    ("Cyprus", "CY", ["Nicosia"]),
    ("Dominica", "DM", []),
    ("Dominican Republic", "DO", ["Santo Domingo"]),
    ("Ecuador", "EC", ["Quito", "Guayaquil"]),
    ("Egypt", "EG", ["Cairo", "Alexandria"]),
    ("El Salvador", "SV", ["San Salvador"]),
    ("Equatorial Guinea", "GQ", []),
    ("Eritrea", "ER", ["Asmara"]),
    ("Eswatini", "SZ", ["Swaziland"]),
    ("Ethiopia", "ET", ["Addis Ababa"]),
    ("Fiji", "FJ", ["Suva"]),
    ("Gabon", "GA", ["Libreville"]),
    ("Gambia", "GM", ["Banjul"]),
    ("Georgia", "GE", ["Tbilisi"]),
    ("Grenada", "GD", []),
    ("Guatemala", "GT", ["Guatemala City"]),
    ("Guinea", "GN", ["Conakry"]),
    ("Guinea-Bissau", "GW", []),
    ("Guyana", "GY", ["Georgetown"]),
    ("Haiti", "HT", ["Port-au-Prince"]),
    ("Honduras", "HN", ["Tegucigalpa"]),
    ("Hungary", "HU", ["Budapest"]),
    ("Indonesia", "ID", ["Jakarta", "Bali", "Surabaya"]),
    ("Iran", "IR", ["Tehran"]),
    ("Iraq", "IQ", ["Baghdad", "Basra", "Mosul"]),
    ("Israel", "IL", ["Tel Aviv", "Jerusalem", "Haifa"]),
    ("Jamaica", "JM", ["Kingston"]),
    ("Jordan", "JO", ["Amman"]),
    ("Kazakhstan", "KZ", ["Astana", "Almaty"]),
    ("Kiribati", "KI", []),
    ("Kosovo", "XK", ["Pristina"]),
    ("Kuwait", "KW", ["Kuwait City"]),
    ("Kyrgyzstan", "KG", ["Bishkek"]),
    ("Laos", "LA", ["Vientiane"]),
    ("Latvia", "LV", ["Riga"]),
    ("Lesotho", "LS", []),
    ("Liberia", "LR", ["Monrovia"]),
    ("Libya", "LY", ["Tripoli", "Benghazi"]),
    ("Liechtenstein", "LI", ["Vaduz"]),
    ("Lithuania", "LT", ["Vilnius", "Kaunas"]),
    ("Luxembourg", "LU", []),
    ("Madagascar", "MG", ["Antananarivo"]),
    ("Malawi", "MW", ["Lilongwe"]),
    ("Malaysia", "MY", ["Kuala Lumpur", "Penang"]),
    ("Maldives", "MV", ["Male"]),
    ("Mali", "ML", ["Bamako", "Timbuktu"]),
    ("Marshall Islands", "MH", []),
    ("Mauritania", "MR", ["Nouakchott"]),
    ("Mauritius", "MU", ["Port Louis"]),
    ("Micronesia", "FM", []),
    ("Moldova", "MD", ["Chisinau"]),
    ("Monaco", "MC", []),
    ("Mongolia", "MN", ["Ulaanbaatar"]),
    ("Montenegro", "ME", ["Podgorica"]),
    ("Morocco", "MA", ["Rabat", "Casablanca", "Marrakech"]),
    ("Mozambique", "MZ", ["Maputo"]),
    ("Myanmar", "MM", ["Burma", "Yangon"]),
    ("Namibia", "NA", ["Windhoek"]),
    ("Nauru", "NR", []),
    ("Nepal", "NP", ["Kathmandu"]),
    ("Nicaragua", "NI", ["Managua"]),
    ("Niger", "NE", ["Niamey"]),
    ("North Korea", "KP", ["Pyongyang"]),
    ("North Macedonia", "MK", ["Macedonia", "Skopje"]),
    ("Oman", "OM", ["Muscat"]),
    ("Pakistan", "PK", ["Islamabad", "Karachi", "Lahore"]),
    ("Palau", "PW", []),
    ("Panama", "PA", ["Panama City"]),
    ("Papua New Guinea", "PG", ["Port Moresby"]),
    ("Paraguay", "PY", ["Asuncion"]),
    ("Peru", "PE", ["Lima", "Cusco"]),
    ("Qatar", "QA", ["Doha"]),
    ("Romania", "RO", ["Bucharest", "Cluj"]),
    ("Russia", "RU", ["Russian Federation", "Moscow", "Saint Petersburg"]),
    ("Rwanda", "RW", ["Kigali"]),
    ("Saint Kitts and Nevis", "KN", []),
    ("Saint Lucia", "LC", []),
    ("Saint Vincent and the Grenadines", "VC", []),
    ("Samoa", "WS", []),
    ("San Marino", "SM", []),
    ("Sao Tome and Principe", "ST", []),
    ("Senegal", "SN", ["Dakar"]),
    ("Serbia", "RS", ["Belgrade"]),
    ("Seychelles", "SC", []),
    ("Sierra Leone", "SL", ["Freetown"]),
    ("Slovakia", "SK", ["Bratislava"]),
    ("Slovenia", "SI", ["Ljubljana"]),
    ("Solomon Islands", "SB", []),
    ("Somalia", "SO", ["Mogadishu"]),
    ("South Sudan", "SS", ["Juba"]),
    ("Sri Lanka", "LK", ["Colombo"]),
    ("Sudan", "SD", ["Khartoum"]),
    ("Suriname", "SR", ["Paramaribo"]),
    ("Taiwan", "TW", ["Taipei"]),
    ("Tajikistan", "TJ", ["Dushanbe"]),
    ("Thailand", "TH", ["Bangkok"]),
    ("Timor-Leste", "TL", ["East Timor"]),
    ("Togo", "TG", ["Lome"]),
    ("Tonga", "TO", []),
    ("Trinidad and Tobago", "TT", ["Port of Spain"]),
    ("Tunisia", "TN", ["Tunis"]),
    ("Turkmenistan", "TM", ["Ashgabat"]),
    ("Tuvalu", "TV", []),
    ("Uganda", "UG", ["Kampala"]),
    ("Uruguay", "UY", ["Montevideo"]),
    ("Uzbekistan", "UZ", ["Tashkent"]),
    ("Vanuatu", "VU", []),
    ("Vatican City", "VA", ["Holy See", "Vatican"]),
    ("Venezuela", "VE", ["Caracas"]),
    ("Yemen", "YE", ["Sanaa", "Aden"]),
    ("Zambia", "ZM", ["Lusaka"]),
    ("Zimbabwe", "ZW", ["Harare"])
]

def main():
    path = "data/lookups/countries.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing = {c["name"].lower(): c for c in data["countries"]}
    existing_codes = {c["code"].upper(): c for c in data["countries"]}

    added = 0
    for name, code, aliases in ADDITIONAL_COUNTRIES:
        if name.lower() in existing or code.upper() in existing_codes:
            # Update aliases if needed
            target = existing.get(name.lower()) or existing_codes.get(code.upper())
            for a in aliases:
                if a not in target["aliases"]:
                    target["aliases"].append(a)
            continue

        data["countries"].append({
            "name": name,
            "code": code,
            "aliases": aliases
        })
        added += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated countries lookup: added {added} new countries, total {len(data['countries'])}.")

if __name__ == "__main__":
    main()
