% preguntas.pl
enfermedad(gato_persas, leucemia_felina).
enfermedad(gato_persas, alergia).

% Reglas para determinar síntomas
sintomas(leucemia_felina, 'fiebre, pérdida de apetito, infecciones recurrentes').
sintomas(alergia, 'picazón, erupciones, estornudos').

% Regla para validar la enfermedad basada en síntomas
diagnostico(Sintoma, Enfermedad) :-
    sintomas(Enfermedad, Sintoma).
