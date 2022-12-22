from gettext import Catalog
import os
from re import sub
from xml.dom.expatbuilder import parseFragmentString
import google

# from google.appengine.ext import vendor
import streamlit as st
from google.oauth2 import service_account
import pandas as pd
import gspread
from pprint import pprint
import gspread_dataframe as gd
from datetime import datetime
import numpy as np
from PIL import Image


class user_interface:
    def __init__(self):
        self.db_connection = db_connection()
        self.quartal = None

    def tab_main(self):

        image = Image.open(os.path.join("chicken.png"))
        st.image(image)

        st.markdown("# Krismer Hendl Bestellungen")
        self.quartal = st.selectbox("Quartal", options= ["2022_Q4"])

        sum = str(self.sum_quartal_hendl(quartal=self.quartal))  
        n = str(self.get_n_orders(quartal=self.quartal)) 
        summary = sum + " Hennen bestellt, " + n + " Bestellungen"
        
        st.markdown(summary)     
       
        st.markdown("Neue Bestellung")
        self.neue_bestellung()
    
    def neue_bestellung(self):
        with st.form("bestellung"):
            vorname = st.text_input("Vorname")
            nachname = st.text_input("Nachname")
            anzahl = st.selectbox(
                "Anzahl", options=[0.5, 1, 1.5, 2, 2.5, 3, 3.5]
            )
            anmerkung = st.text_input("Anmerkung")
            telefonnummer = st.text_input("Telefonnummer")

            submitted = st.form_submit_button("Neue Bestellung hinzufügen")

            if submitted:
                date_added = datetime.today().strftime("%Y-%m-%d")
                new_order_list = [
                    vorname,
                    nachname,
                    anzahl,
                    anmerkung,
                    telefonnummer,
                    date_added
                ]

                self.db_connection.add_new_order(new_order_list, quartal=self.quartal)
                st.info("Bestellung wurde gespeichert.")


    def sum_quartal_hendl(self, quartal):
        df = self.db_connection.get_df_quartal(quartal)
        sum = df["Anzahl"].sum()
        return sum
    
    def get_n_orders(self, quartal):
        df = self.db_connection.get_df_quartal(quartal)
        n = df.shape[0]
        return n


    def tab_overview_orders(self):
        quartal = st.selectbox("Quartal", options=["2022_Q4"])
        df = self.db_connection.get_df_quartal(quartal)
        st.markdown("## übersicht")
        st.dataframe(df.astype(str), height=900)


class db_connection:
    def __init__(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive",
        ]

        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scope
        )
        client = gspread.authorize(credentials)
        self.client = client

    def get_df_quartal(self, quartal):
        sheet = self.client.open("Bestellungen").worksheet(quartal)
        df = pd.DataFrame(sheet.get_all_records())
        return df

    def add_new_order(self, row, quartal):
        sheet = self.client.open("Bestellungen").worksheet(quartal)
        sheet.append_row(row)

    def get_options(self, column):
        input_options = self.client.open("LabData").worksheet("Options")
        input_options_df = gd.get_as_dataframe(input_options)
        # remove numpy nans
        options = ["None"] + list(set(input_options_df[column].dropna().to_list()))
        return options


def run():
    ui = user_interface()

    radio = st.sidebar.radio(
        "Navigation",
        options=[
            "Main",
            "übersicht",
        ],
    )

    if radio == "Main":
        ui.tab_main()

    elif radio == "übersicht":
        ui.tab_overview_orders()

    else:
        return


if __name__ == "__main__":
    run()
