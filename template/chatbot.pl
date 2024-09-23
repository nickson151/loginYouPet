% chatbot.pl

% Cargar la base de datos de preguntas
:- [preguntas].

% Reglas para determinar la enfermedad basada en los síntomas mencionados
responder_pregunta(Pregunta, Respuesta) :-
    (   diagnostico(Pregunta, Enfermedad)
    ->  Respuesta = ['La enfermedad más probable es ', Enfermedad]
    ;   Respuesta = ['No tengo suficiente información para determinar la enfermedad.']
    ).
