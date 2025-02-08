import asyncio
from medical_recommender import AdvancedMedicalPredictor
from medical_predictor import MedicalPredictor, load_training_data

async def run_advanced_predictor():
    predictor2 = AdvancedMedicalPredictor('output.json')
    prediction = predictor2.predict_single(
        age=35,
        gender='M',
        symptoms='Fever, Cough, Headache',
        cause='Viral Infection'
    )


    print(type(prediction))
    print(prediction)
async def run_basic_predictor():
    training_data = load_training_data('output.json')
    predictor = MedicalPredictor()
    predictor.train(training_data)
    
    age = 40
    gender = 'M'
    symptoms = 'Fever, Cough'
    cause = 'Viral Infection'
    
    diseases, medicines = predictor.predict(age, gender, symptoms, cause)
    
    print(type(diseases))
    print(diseases)
    print(type(medicines))
    print(medicines)

async def main():
    # Run both predictors concurrently
    await asyncio.gather(
        run_advanced_predictor(),
        run_basic_predictor()
    )

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())