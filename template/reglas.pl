% rules.pl
responder_pregunta(Pregunta, Respuesta) :-
    % Definir la lógica para responder preguntas basadas en la entrada
    % Ejemplo simple:
    (Pregunta = '¿Cuáles son los síntomas de la leucemia felina?' ->
        Respuesta = 'fiebre, pérdida de apetito, infecciones recurrentes';
    Pregunta = '¿Qué es la alergia?' ->
        Respuesta = 'picazón, erupciones, estornudos';
    Respuesta = 'No sé la respuesta.')
