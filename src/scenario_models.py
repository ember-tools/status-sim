"""Pydantic-Modelle zum Definieren und Laden von Alarm-Szenarien aus JSON.

Die JSON-Dateien enthalten nur Metainformationen. Die Funksprüche werden
daraus generiert.
"""

from typing import Dict, List, Literal, Optional, Union, Annotated, Tuple
from unittest import case

from pydantic import BaseModel, Field
import random


class Einheit(BaseModel):
    """Eine Einheit (z.B. C-Dienst, NEF, RTW, DLK, LHF)."""
    typ: str
    anzahl: int = 1
    kennung: Optional[str] = None

    def _generate_single_name(self) -> str:
        if self.kennung and self.anzahl == 1:
            return self.kennung
        return f"{self._type_name()} {self._generate_number()}"

    def _generate_number(self):
        num = random.choice([n for n in range(11, 66) if n % 10 != 0])
        x = random.randint(1, 6)
        match self.typ:
            case "FD" | "ELWC":
                return f"{num}17"
            case "FD" | "ELWB":
                return f"{num}17"
            case "NEF":
                return f"{num}05"
            case "RTW":
                return f"{num}00/{x}"
            case _:
                return f"{num}00/1"

    def _type_name(self):
        match self.typ:
            case "FD" | "ELWC" | "ELWB":
                return f"ELW"
            case _:
                return f"{self.typ}"

    def get_fahrzeug_name(self):
        match self.typ:
            case "FD" | "ELWC":
                return "C-Dienst"
            case _:
                return self.typ

    def generate_names(self) -> List[str]:
        if self.kennung and self.anzahl == 1:
            return [self.kennung]
        names = set()
        while len(names) < max(1, self.anzahl):
            names.add(self._generate_number())
        names = list(names)
        names[0] = f"{self._type_name()} {names[0]}"
        return names


class FunkEntry(BaseModel):
    actor: Literal["LS", "SF", "FZ"]
    message: Optional[str] = None
    status: Optional[str] = None


class FunkContext(BaseModel):
    fk: str
    ls: str
    einsatz_adresse: str
    einsatz_ortsteil: str
    einsatz_stichwort: str
    enr_counter: int = 1

    def next_enr(self) -> str:
        val = str(self.enr_counter)
        self.enr_counter += random.randint(5, 15)
        return val


class Lagemeldung(BaseModel):
    """Lagemeldung in der richtigen Reihenfolge (wird für SF geshuffled)."""
    lage: Optional[str] = "Einsatzstelle unter Kontrolle (EstuK)"
    geraete: Optional[str] = None
    beschreibung: Optional[str] = None
    verletzte: Optional[str] = "Keine Verletzten"
    uebergabe: Optional[str] = None


class EigenunfallSchritt(BaseModel):
    """Eigenunfall während der Anfahrt."""
    typ: Literal["eigenunfall"]
    mit_personenschaden: bool
    verletzte: int = 1
    adresse: str
    ortsteil: str

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        e: List[FunkEntry] = []
        if self.mit_personenschaden:
            rtw_namen = Einheit(typ="RTW", anzahl=max(1, self.verletzte)).generate_names()
            cd_name = Einheit(typ="FD").generate_names()[0]
            rtw_liste = ", ".join(rtw_namen)
            e += [
                FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
                FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
                FunkEntry(actor="SF",
                          message=f"Wir hatten einen Unfall mit Personenschaden {self.verletzte}, {self.adresse} {self.ortsteil}, Quittung kommen."),
                FunkEntry(actor="FZ",
                          message=f"Wir hatten einen Unfall mit Personenschaden {self.verletzte}, {self.adresse} {self.ortsteil}, kommen."),
                FunkEntry(actor="SF", message="So richtig, Ende."),
                FunkEntry(actor="FZ", status="0"),
                FunkEntry(actor="LS", message=f"Florian {ctx.fk} Blitz, kommen."),
                FunkEntry(actor="FZ", message=f"Hier {ctx.fk} mit Eigenunfall mit Personenschaden, kommen."),
                FunkEntry(actor="LS", message="Wo befinden sie sich, kommen."),
                FunkEntry(actor="FZ", message=f"{self.adresse} {self.ortsteil}, kommen."),
                FunkEntry(actor="LS", message=f"{self.adresse} {self.ortsteil}, so recht? Kommen."),
                FunkEntry(actor="FZ", message="So richtig, kommen."),
                FunkEntry(actor="LS", message="Wie viele Verletzte, kommen."),
                FunkEntry(actor="FZ", message=f"Verletzte: {self.verletzte}, kommen."),
                FunkEntry(actor="LS",
                          message=f"Verstanden, sie dann in Status 4, {rtw_liste} und {cd_name} sind auf dem Weg, {ctx.ls} <time> Ende."),
                FunkEntry(actor="FZ", status="4"),
            ]
        else:
            cd_name = Einheit(typ="FD").generate_names()[0]
            e += [
                FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
                FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
                FunkEntry(actor="SF",
                          message=f"Wir hatten einen Unfall ohne Personenschaden, {self.adresse} {self.ortsteil}, Quittung kommen."),
                FunkEntry(actor="FZ",
                          message=f"Wir hatten einen Unfall ohne Personenschaden, {self.adresse} {self.ortsteil}, kommen."),
                FunkEntry(actor="SF", message="So richtig, Ende"),
                FunkEntry(actor="SF", status="0"),
                FunkEntry(actor="LS", message=f"Florian {ctx.fk} Blitz, kommen."),
                FunkEntry(actor="FZ", message=f"Hier {ctx.fk} mit Eigenunfall ohne Personenschaden, kommen."),
                FunkEntry(actor="LS", message="Wo befinden sie sich, kommen."),
                FunkEntry(actor="FZ", message=f"{self.adresse} {self.ortsteil}, kommen."),
                FunkEntry(actor="LS", message=f"{self.adresse} {self.ortsteil}, so recht? Kommen."),
                FunkEntry(actor="FZ", message="So richtig, kommen."),
                FunkEntry(actor="LS",
                          message=f"Verstanden, sie dann in Status 4, {cd_name} ist auf dem Weg, {ctx.ls} <time> Ende."),
                FunkEntry(actor="SF", status="4"),
            ]
        return e


class EigenunfallStatus1Schritt(BaseModel):
    """Eigenunfall während der Anfahrt in Status 1."""
    typ: Literal["eigenunfall_status_1"]
    mit_personenschaden: bool
    verletzte: int = 1
    adresse: str
    ortsteil: str

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        cd_name = Einheit(typ="FD").generate_names()[0]
        e: List[FunkEntry] = []
        if self.mit_personenschaden:
            rtw_namen = Einheit(typ="RTW", anzahl=max(1, self.verletzte)).generate_names()
            rtw_liste = ", ".join(rtw_namen)
            e += [
                FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
                FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
                FunkEntry(actor="SF",
                          message=f"Wir hatten einen Unfall mit Personenschaden {self.verletzte}, {self.adresse} {self.ortsteil}, Quittung kommen."),
                FunkEntry(actor="FZ",
                          message=f"Wir hatten einen Unfall mit Personenschaden {self.verletzte}, {self.adresse} {self.ortsteil}, kommen."),
                FunkEntry(actor="SF", message="So richtig, Ende."),
                FunkEntry(actor="FZ", status="3"),
                FunkEntry(actor="FZ", status="0"),
                FunkEntry(actor="LS", message=f"Florian {ctx.fk} Blitz, kommen."),
                FunkEntry(actor="FZ", message=f"Hier {ctx.fk} mit Eigenunfall mit Personenschaden, kommen."),
                FunkEntry(actor="LS", message="Wo befinden sie sich, kommen."),
                FunkEntry(actor="FZ", message=f"{self.adresse} {self.ortsteil}, kommen."),
                FunkEntry(actor="LS", message=f"{self.adresse} {self.ortsteil}, so recht? Kommen."),
                FunkEntry(actor="FZ", message="So richtig, kommen."),
                FunkEntry(actor="LS", message="Wie viele Verletzte, kommen."),
                FunkEntry(actor="FZ", message=f"Verletzte: {self.verletzte}, kommen."),
                FunkEntry(actor="LS",
                          message=f"Verstanden, sie dann in Status 4, {rtw_liste} und {cd_name} sind auf dem Weg, {ctx.ls} <time> Ende."),
                FunkEntry(actor="FZ", status="4"),
            ]
        else:
            return [
                FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
                FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
                FunkEntry(actor="SF",
                          message=f"Wir hatten einen Unfall ohne Personenschaden, {self.adresse} {self.ortsteil}, Quittung kommen."),
                FunkEntry(actor="FZ",
                          message=f"Wir hatten einen Unfall ohne Personenschaden, {self.adresse} {self.ortsteil}, kommen."),
                FunkEntry(actor="SF", message="So richtig, Ende"),
                FunkEntry(actor="SF", status="3"),
                FunkEntry(actor="SF", status="5"),
                FunkEntry(actor="LS", message=f"Florian {ctx.fk} Blitz, kommen."),
                FunkEntry(actor="FZ", message=f"Hier {ctx.fk} mit Eigenunfall ohne Personenschaden, kommen."),
                FunkEntry(actor="LS", message="Wo befinden sie sich, kommen."),
                FunkEntry(actor="FZ", message=f"{self.adresse} {self.ortsteil}, kommen."),
                FunkEntry(actor="LS", message=f"{self.adresse} {self.ortsteil}, so recht? Kommen."),
                FunkEntry(actor="FZ", message="So richtig, kommen."),
                FunkEntry(actor="LS",
                          message=f"Verstanden, sie dann in Status 4, {cd_name} ist auf dem Weg, {ctx.ls} <time> Ende."),
                FunkEntry(actor="SF", status="4"),
            ]


class NeueTaetigkeitMitFznSchritt(BaseModel):
    """Neue Tätigkeit mit Fahrzeugnennung während der Anfahrt."""
    typ: Literal["neue_taetigkeit_mit_fzn"]
    fahrzeuge: Optional[list[Einheit]] = None
    ereignis: str
    sonderrechte: Optional[bool] = True
    adresse: str
    ortsteil: str

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        last = FunkEntry(actor="LS",
                         message=f"Verstanden, Einsatz unter Nummer {ctx.next_enr()} angelegt. Sie dann weiter mit Status 4, {ctx.ls} <time> Ende.")
        if self.fahrzeuge:
            fz_liste, fz_namen = generate_names(self.fahrzeuge)
            last = FunkEntry(actor="LS",
                      message=f"Verstanden, Einsatz unter Nummer {ctx.next_enr()} angelegt. {fz_liste} unterwegs. Sie dann weiter mit Status 4, {ctx.ls} <time> Ende.")


        e: List[FunkEntry] = [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF",
                      message=f"Wir haben eine neue Tätigkeit mit Fahrzeugnennung, {self.adresse} {self.ortsteil}, {self.ereignis}, kommen."),
            FunkEntry(actor="FZ",
                      message=f"Verstanden, neue Tätigkeit mit Fahrzeugnennung, {self.adresse} {self.ortsteil}, {self.ereignis}, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="FZ", status="0" if self.sonderrechte else "5"),
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} Sprechwunsch, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Florian {ctx.fk} mit neuer Tätigkeit mit Fahrzeugnennung, kommen."),
            FunkEntry(actor="LS", message="Wo befinden sie sich und das Ereignis, kommen."),
            FunkEntry(actor="FZ", message=f"{self.adresse} {self.ortsteil}, {self.ereignis}, kommen."),
            FunkEntry(actor="LS", message=f"{self.adresse} {self.ortsteil}, {self.ereignis} so recht, kommen."),
            FunkEntry(actor="FZ", message="So richtig, kommen."),
            last,
            FunkEntry(actor="FZ", status="4"),
        ]
        return e


class NeueTaetigkeitMitFznStatus1Schritt(BaseModel):
    """Neue Tätigkeit mit Fahrzeugnennung während der Anfahrt aus Status 1."""
    typ: Literal["neue_taetigkeit_mit_fzn_status_1"]
    fahrzeuge: Optional[list[Einheit]] = None
    sonderrechte: Optional[bool] = True
    ereignis: str
    adresse: str
    ortsteil: str

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        last = FunkEntry(actor="LS",
                         message=f"Verstanden, Einsatz unter Nummer {ctx.next_enr()} angelegt. Sie dann weiter mit Status 4, {ctx.ls} <time> Ende.")
        if self.fahrzeuge:
            fz_liste, _ = generate_names(self.fahrzeuge)
            last = FunkEntry(actor="LS",
                      message=f"Verstanden, Einsatz unter Nummer {ctx.next_enr()} angelegt. {fz_liste} unterwegs. Sie dann weiter mit Status 4, {ctx.ls} <time> Ende.")

        return [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF",
                      message=f"Eigenmeldung mit Fahrzeugnennung, {self.adresse} {self.ortsteil}, {self.ereignis}, kommen."),
            FunkEntry(actor="FZ",
                      message=f"Verstanden, Eigenmeldung mit Fahrzeugnennung, {self.adresse} {self.ortsteil}, {self.ereignis}, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="FZ", status="3"),
            FunkEntry(actor="FZ", status="0" if self.sonderrechte else "5"),
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} Sprechwunsch, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Florian {ctx.fk} mit neuer Tätigkeit mit Fahrzeugnennung, kommen."),
            FunkEntry(actor="LS", message="Wo befinden sie sich und das Ereignis, kommen."),
            FunkEntry(actor="FZ", message=f"{self.adresse} {self.ortsteil}, {self.ereignis}, kommen."),
            FunkEntry(actor="LS", message=f"{self.adresse} {self.ortsteil}, {self.ereignis} so recht, kommen."),
            FunkEntry(actor="FZ", message="So richtig, kommen."),
            last,
            FunkEntry(actor="FZ", status="4"),
        ]


class NeueTaetigkeitOhneFznSchritt(BaseModel):
    """Neue Tätigkeit ohne Fahrzeugnennung während der Anfahrt."""
    typ: Literal["neue_taetigkeit_ohne_fzn"]
    ereignis: str
    adresse: str
    ortsteil: str

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        return [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF",
                      message=f"Eigenmeldung ohne Fahrzeugnennung, {self.adresse} {self.ortsteil}, {self.ereignis}, kommen."),
            FunkEntry(actor="FZ",
                      message=f"Verstanden, Eigenmeldung ohne Fahrzeugnennung, {self.adresse} {self.ortsteil}, {self.ereignis}, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="FZ", status="0"),
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} Sprechwunsch, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Florian {ctx.fk} mit Eigenmeldung ohne Fahrzeugnennung, kommen."),
            FunkEntry(actor="LS", message="Wo befinden sie sich und das Ereignis, kommen."),
            FunkEntry(actor="FZ", message=f"{self.adresse} {self.ortsteil}, {self.ereignis}, kommen."),
            FunkEntry(actor="LS", message=f"{self.adresse} {self.ortsteil}, {self.ereignis} so recht, kommen."),
            FunkEntry(actor="FZ", message="So recht, kommen."),
            FunkEntry(actor="LS", message=f"Verstanden, {ctx.ls} <time> Ende."),
        ]

class IdentischeAdresse(BaseModel):
    """Eine Adresse bestehend aus Straße/Hausnummer und Ortsteil."""
    typ: Optional[str] = None
    adresse: Optional[str] = None
    ortsteil: Optional[str] = None
    identisch: Optional[bool] = None

class IdentischeEinsatzstelleAnfrageSchritt(BaseModel):
    """Nachfrage nach einer identischen Einsatzstelle."""
    typ: Literal["identische_einsatzstelle_anfrage"]
    adressen: List[IdentischeAdresse]
    stichwort_typ : str = "Brand"

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        ls_frage = f"Der Leitstelle liegen weitere Meldungen über einen {self.stichwort_typ} vor – "
        adr_strings = [f"{a.adresse} in {a.ortsteil}" for a in self.adressen]
        if len(adr_strings) > 1:
            ls_frage += " und ".join([", ".join(adr_strings[:-1]), adr_strings[-1]])
        else:
            ls_frage += adr_strings[0]

        ls_mitteilung = ls_frage
        
        ls_frage += " – Frage: sind diese Meldungen mit ihrer Einsatzstelle identisch? – kommen"

        fz_antwort_identisch = []
        sf_antwort_identisch = []
        for a in self.adressen:
            status = "ist identisch" if a.identisch else "ist mit der Einsatzstelle nicht identisch"
            fz_antwort_identisch.append(f"Die Meldung {a.adresse} {a.ortsteil} {status}")
            sf_antwort_identisch.append(f"{a.adresse} {status}")
        
        fz_antwort_identisch_str = " – ".join(fz_antwort_identisch)
        sf_antwort_identisch_str = " – ".join(sf_antwort_identisch)

        return [
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} von {ctx.ls}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Florian {ctx.fk}, kommen."),
            FunkEntry(actor="LS", message=ls_frage),
            FunkEntry(actor="FZ", message=f"{ls_mitteilung} Ich halte Nachfrage, kommen."),
            FunkEntry(actor="LS", message=f"Verstanden, {ctx.ls} <time>, Ende."),
            
            FunkEntry(actor="FZ", message=f"Staffelführer {ctx.fk} von Melder {ctx.fk} kommen."),
            FunkEntry(actor="SF", message=f"Hier Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"{ls_mitteilung} Frage: Sind diese Meldungen identisch? Kommen."),
            FunkEntry(actor="SF", message=f"Schaue nach, komme neu, kommen."),
            FunkEntry(actor="FZ", message=f"So recht, Ende."),

            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk} kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF", message=f"{sf_antwort_identisch_str}, kommen."),
            FunkEntry(actor="FZ", message=f"{sf_antwort_identisch_str}, kommen."),
            FunkEntry(actor="SF", message=f"So recht, Ende."),

            FunkEntry(actor="FZ", status="0"),
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} Sprechwunsch, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Florian {ctx.fk} zur Nachfrage der weiteren Einsatzstellen, kommen."),
            FunkEntry(actor="FZ", message=f"{fz_antwort_identisch_str} – kommen."),
            FunkEntry(actor="LS", message=f"Verstanden, {ctx.ls} <time>, Ende."),
        ]


class EinsatzstellenkorrekturSchritt(BaseModel):
    """Einsatzstellenkorrektur während der Anfahrt."""
    typ: Literal["einsatzstellenkorrektur"]
    adresse: str
    ortsteil: str

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        return [
            FunkEntry(actor="LS", message=f"Florian {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Florian {ctx.fk}, kommen."),
            FunkEntry(actor="LS", message="Wir haben eine Einsatzstellenkorrektur, kommen."),
            FunkEntry(actor="FZ", message="Anfangen, kommen."),
            FunkEntry(actor="LS", message=f"{self.adresse} {self.ortsteil}, Quittung kommen."),
            FunkEntry(actor="FZ", message=f"{self.adresse} {self.ortsteil}, kommen."),
            FunkEntry(actor="LS", message=f"So richtig, {ctx.ls} <time> Ende."),
            FunkEntry(actor="FZ", message=f"Staffelführer {ctx.fk} von Melder {ctx.fk} kommen."),
            FunkEntry(actor="SF", message=f"Hier Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ",
                      message=f"Einsatzstellenkorrektur auf {self.adresse} {self.ortsteil}, Quittung kommen."),
            FunkEntry(actor="SF",
                      message=f"Einsatzstellenkorrektur auf {self.adresse} {self.ortsteil} verstanden, kommen."),
            FunkEntry(actor="FZ", message="So richtig, Ende."),
        ]


class AnkommenSchritt(BaseModel):
    """Ankommen ohne Ereignis."""
    typ: Literal["ankommen"]

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        return [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF", message="Wir sind an der Einsatzstelle eingetroffen, Quittung kommen."),
            FunkEntry(actor="FZ", message="Wir sind an der Einsatzstelle eingetroffen, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="FZ", status="4"),
        ]


class KurzlagemeldungFMSSchritt(BaseModel):
    """Kurzlagemeldung über FMS an der Einsatzstelle."""
    typ: Literal["kurzlagemeldung_fms"]
    text: str

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        return [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF", message=f"Kurzlagemeldung {self.text}, Quittung kommen."),
            FunkEntry(actor="FZ", message=f"Kurzlagemeldung {self.text}, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="FZ", message="Kurzlagemeldung erteilt"),
        ]


class KurzlagemeldungSchritt(BaseModel):
    """Kurzlagemeldung mündlich über Status 5."""
    typ: Literal["kurzlagemeldung"]
    text: str

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        return [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF", message=f"Kurzlagemeldung, {self.text}, Quittung kommen."),
            FunkEntry(actor="FZ", message=f"Kurzlagemeldung, {self.text}, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="SF", status="5"),
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} Sprechwunsch, kommen."),
            FunkEntry(actor="FZ", message=f"Florian {ctx.fk} mit Kurzlage, kommen."),
            FunkEntry(actor="FZ", message=f"Lage ist, kommen."),
            FunkEntry(actor="FZ", message=f"{self.text}, kommen."),
            FunkEntry(actor="LS", message=f"Verstanden, {ctx.ls} <time> Ende."),
        ]


class LagemeldungSchritt(BaseModel):
    """Abschließende Lagemeldung (Mit Lagemeldung)."""
    typ: Literal["lagemeldung"]
    lagemeldung: Lagemeldung

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        lm = self.lagemeldung

        def filter_lm_parts(lm_obj: Lagemeldung) -> List[str]:
            parts = []
            if lm_obj.lage:
                parts.append(lm_obj.lage)
            if lm_obj.geraete:
                parts.append(lm_obj.geraete)
            if lm_obj.beschreibung:
                parts.append(lm_obj.beschreibung)
            if lm_obj.verletzte and lm_obj.verletzte.lower() != "keine verletzten":
                parts.append(lm_obj.verletzte)
            if lm_obj.uebergabe:
                parts.append(lm_obj.uebergabe)
            return parts

        teile_sf = filter_lm_parts(lm)
        random.shuffle(teile_sf)

        ls_parts = []
        if lm.lage:
            ls_parts.append(lm.lage)
        if lm.geraete:
            ls_parts.append(lm.geraete)
        if lm.beschreibung:
            ls_parts.append(lm.beschreibung)
        if lm.verletzte and lm.verletzte.lower() != "keine verletzten":
            ls_parts.append(lm.verletzte)
        if lm.uebergabe:
            ls_parts.append(lm.uebergabe)

        ls_msg = f"{ctx.einsatz_adresse} {ctx.einsatz_ortsteil}, {', '.join(ls_parts)}, Staffelführer {ctx.fk}, kommen."

        return [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF", message="Mit Lagemeldung, kommen."),
            FunkEntry(actor="FZ", message="Lage ist, kommen."),
            FunkEntry(actor="SF", message=f"{', '.join(teile_sf)}, kommen."),
            FunkEntry(actor="FZ", message=f"{', '.join(teile_sf)}, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="FZ", status="5"),
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} Sprechwunsch, kommen."),
            FunkEntry(actor="FZ", message="Mit Lagemeldung, kommen."),
            FunkEntry(actor="LS", message="Lage ist, kommen."),
            FunkEntry(actor="FZ", message=ls_msg),
            FunkEntry(actor="LS", message=f"Verstanden, {ctx.ls} <time> Ende."),
            FunkEntry(actor="FZ", message=f"Staffelführer {ctx.fk} von Melder {ctx.fk} kommen."),
            FunkEntry(actor="SF", message=f"Hier Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message="Lagemeldung abgegeben, kommen."),
            FunkEntry(actor="SF", message="Verstanden, wir wieder status 1 kommen."),
            FunkEntry(actor="FZ", message="Status 1 verstanden, Ende."),
            FunkEntry(actor="FZ", status="1"),
        ]


class OhneLagemeldungSchritt(BaseModel):
    """Einsatz beendet ohne Lagemeldung."""
    typ: Literal["ohne_lagemeldung"]

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        return [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF", message="Einsatz beendet, wir wieder Status 1, kommen."),
            FunkEntry(actor="FZ", message="Status 1 verstanden, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="FZ", status="1"),
        ]


class NachalarmierungFahrzeugeSchritt(BaseModel):
    """Nachalarmierung von spezifischen Fahrzeugen an der Einsatzstelle.

    `fahrzeuge` are the vehicles alerted in addition.
    """
    typ: Literal["nachalarmierung_fahrzeuge"]
    fahrzeuge: List[Einheit]
    begruendung: str

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        fz_liste, fz_names = generate_names(self.fahrzeuge)

        return [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF", message=f"Nachalarmierung {fz_names}, {self.begruendung}, Quittung kommen."),
            FunkEntry(actor="FZ", message=f"Nachalarmierung {fz_names}, {self.begruendung}, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="FZ", status="0"),
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} Blitz, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Florian {ctx.fk} mit Nachalarmierung {fz_names}, kommen."),
            FunkEntry(actor="LS", message=f"Begründung für {fz_names}, kommen."),
            FunkEntry(actor="FZ", message=f"{self.begruendung}, kommen."),
            FunkEntry(actor="LS", message=f"Verstanden {fz_liste} unterwegs, {ctx.ls} <time> Ende."),
        ]


class NachalarmierungSchritt(BaseModel):
    """Nachalarmierung an der Einsatzstelle.

    `fahrzeuge` are the vehicles the additional alerting brings along, if any.
    """
    typ: Literal["nachalarmierung"]
    fahrzeuge: Optional[List[Einheit]] = None
    stichwort: str
    begruendung: str

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        last = FunkEntry(actor="LS", message=f"Verstanden, {ctx.ls} <time> Ende."),

        if self.fahrzeuge:
            fz_liste, fz_names = generate_names(self.fahrzeuge)
            last = FunkEntry(actor="LS", message=f"Verstanden {fz_liste} unterwegs, {ctx.ls} <time> Ende."),

        return [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF", message=f"Nachalarmierung auf {self.stichwort} {self.begruendung}, Quittung kommen."),
            FunkEntry(actor="FZ", message=f"Nachalarmierung auf {self.stichwort} {self.begruendung}, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="FZ", status="0"),
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} Blitz, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Florian {ctx.fk} mit Nachalarmierung auf {self.stichwort}, kommen."),
            FunkEntry(actor="LS", message=f"Begründung für {self.stichwort}, kommen."),
            FunkEntry(actor="FZ", message=f"{self.begruendung}, kommen."),
            last,
        ]


class FehlalarmLagemeldungSchritt(BaseModel):
    """Lagemeldung bei Fehlalarm BMA."""
    typ: Literal["fehlalarm_lagemeldung"]

    def generate_entries(self, ctx: FunkContext) -> List[FunkEntry]:
        return [
            FunkEntry(actor="SF", message=f"Melder {ctx.fk} von Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Melder {ctx.fk}, kommen."),
            FunkEntry(actor="SF", message="Mit Lagemeldung, kommen."),
            FunkEntry(actor="FZ", message="Lage ist, kommen."),
            FunkEntry(actor="SF", message="Fehlalarm BMA, kommen."),
            FunkEntry(actor="FZ", message="Fehlalarm BMA, kommen."),
            FunkEntry(actor="SF", message="So richtig, Ende."),
            FunkEntry(actor="FZ", status="5"),
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} Sprechwunsch, kommen."),
            FunkEntry(actor="FZ", message="Mit Lagemeldung, kommen."),
            FunkEntry(actor="LS", message="Lage ist, kommen."),
            FunkEntry(actor="FZ",
                      message=f"{ctx.einsatz_adresse}, {ctx.einsatz_ortsteil}, Fehlalarm BMA, Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="LS", message=f"Verstanden, {ctx.ls} <time> Ende."),
            FunkEntry(actor="FZ", message=f"Staffelführer {ctx.fk} von Melder {ctx.fk} kommen."),
            FunkEntry(actor="SF", message=f"Hier Staffelführer {ctx.fk} von Melder {ctx.fk}, kommen."),
            FunkEntry(actor="FZ", message="Lagemeldung abgegeben, kommen."),
            FunkEntry(actor="SF", message="Verstanden, wir wieder status 1 kommen."),
            FunkEntry(actor="FZ", message="Status 1 verstanden, Ende."),
            FunkEntry(actor="FZ", status="1"),
        ]


from typing import Union

Schritt = Union[
    "EigenunfallSchritt",
    "EigenunfallStatus1Schritt",
    "NeueTaetigkeitMitFznSchritt",
    "NeueTaetigkeitMitFznStatus1Schritt",
    "NeueTaetigkeitOhneFznSchritt",
    "EinsatzstellenkorrekturSchritt",
    "AnkommenSchritt",
    "KurzlagemeldungFMSSchritt",
    "KurzlagemeldungSchritt",
    "LagemeldungSchritt",
    "OhneLagemeldungSchritt",
    "NachalarmierungSchritt",
    "NachalarmierungFahrzeugeSchritt",
    "FehlalarmLagemeldungSchritt",
    "IdentischeEinsatzstelleAnfrageSchritt",
]


class Einsatz(BaseModel):
    """Ein einzelner Einsatz innerhalb eines Szenarios."""
    stichwort: str
    adresse: str
    ortsteil: str
    einheiten: List[Einheit] = Field(default_factory=list)
    schritte: List[Annotated[Schritt, Field(discriminator="typ")]]
    einsatznummer: Optional[str] = None

    def generate_alarmierung(self, ctx: FunkContext) -> List[FunkEntry]:
        einheiten_namen: List[str] = []
        for e in self.einheiten:
            einheiten_namen.extend(e.generate_names())
        relevant = [n for n in einheiten_namen if n.startswith("ELW") or n.startswith("NEF")]
        zusatz = f" {', '.join(relevant)}" if relevant else ""
        zusatz_voll = f" {', '.join(einheiten_namen)}" if einheiten_namen else ""
        enr_str = self.einsatznummer or ctx.next_enr()
        return [
            FunkEntry(actor="LS", message=f"Florian {ctx.fk} mit Blitz, kommen."),
            FunkEntry(actor="FZ", message=f"Hier Florian {ctx.fk}, kommen."),
            FunkEntry(actor="LS",
                      message=f"Alarm für {ctx.fk} {zusatz_voll} {self.stichwort}, {self.adresse}, {self.ortsteil} Einsatznummer {enr_str} Alarmierungszeit <time>, Quittung kommen."),
            FunkEntry(actor="FZ",
                      message=f"Einsatznummer {enr_str} {self.stichwort}, {self.adresse} in {self.ortsteil} {zusatz}, kommen."),
            FunkEntry(actor="LS", message=f"So richtig, {ctx.ls} <time> Ende."),
            FunkEntry(actor="FZ", status="3"),
            FunkEntry(actor="FZ", message=f"Staffelführer {ctx.fk} von Melder {ctx.fk} kommen."),
            FunkEntry(actor="SF", message=f"Hier Staffelführer {ctx.fk}, kommen."),
            FunkEntry(actor="FZ",
                      message=f"Neuer Alarm, {self.stichwort}, {self.adresse} in {self.ortsteil}{zusatz}, Quittung kommen."),
            FunkEntry(actor="SF",
                      message=f"Neuer Alarm, {self.stichwort}, {self.adresse} in {self.ortsteil}{zusatz}, kommen."),
            FunkEntry(actor="FZ", message="So richtig, Ende."),
        ]


class Scenario(BaseModel):
    """Ein komplettes Szenario bestehend aus einem oder mehreren Einsätzen."""
    name: str
    beschreibung: str
    einsaetze: List[Einsatz]

    def generate_funksprueche(self, fk: str = "FK-01", ls: str = "LS", start_enr: int = 1) -> List[FunkEntry]:
        """Generate the radio messages of all incidents, each prefixed with `[[E<incident>]][[S<step>]]`.

        Step 0 is the alerting; the scenario steps count from 1. An incident that follows a new task
        of the vehicle gets no alerting of its own.
        """
        ctx = FunkContext(
            fk=fk, ls=ls,
            einsatz_adresse="", einsatz_ortsteil="", einsatz_stichwort="",
            enr_counter=start_enr,
        )
        result: List[FunkEntry] = []
        last_step_type = None
        for i, einsatz in enumerate(self.einsaetze):
            ctx.einsatz_adresse = einsatz.adresse
            ctx.einsatz_ortsteil = einsatz.ortsteil
            ctx.einsatz_stichwort = einsatz.stichwort

            new_activity_types = ["neue_taetigkeit_mit_fzn", "neue_taetigkeit_mit_fzn_status_1", "neue_taetigkeit_ohne_fzn"]
            if last_step_type not in new_activity_types:
                alarm_entries = einsatz.generate_alarmierung(ctx)
                for entry in alarm_entries:
                    prefix = f"[[E{i}]][[S0]]"
                    entry.message = prefix + (entry.message or "")
                    result.append(entry)

            for j, schritt in enumerate(einsatz.schritte):
                gen = getattr(schritt, "generate_entries", None)
                if callable(gen):
                    s_entries = gen(ctx)
                    for entry in s_entries:
                        prefix = f"[[E{i}]][[S{j + 1}]]"
                        entry.message = prefix + (entry.message or "")
                        result.append(entry)
                
                last_step_type = getattr(schritt, "typ", None)

        return result

def generate_names(fahrzeuge: list[Einheit]) -> Tuple[str, str]:
    einheiten_namen: List[str] = []
    fahrzeug_namen = []
    for e in fahrzeuge:
        if e.anzahl < 1:
            continue
        einheiten_namen.extend(e.generate_names())
        fahrzeug_namen.append(f"{e.anzahl} {e.get_fahrzeug_name()}")
    fz_liste = ", ".join(einheiten_namen)
    fz_namen = ", ".join(fahrzeug_namen)
    return fz_liste, fz_namen

