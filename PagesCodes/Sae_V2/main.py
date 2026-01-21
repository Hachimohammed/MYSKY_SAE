from app import app
from app.models.BDDao import DatabaseInit  # Importe ta classe

if __name__ == "__main__":
    # ÉTAPE CRUCIALE : On force la création des tables au lancement
    print("Vérification de la base de données...")
    DatabaseInit() 
    
    # Ensuite on lance Flask 
    # PS vaut mieux (beaucoup mieux) d'executer via cmd et sudo tout est expliquer dans lecteurDAO
    app.run(debug=True)
