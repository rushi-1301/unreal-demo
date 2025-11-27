import io
import logging
import uuid

from collections import deque
from dataclasses import dataclass
from random import shuffle
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from googletrans import Translator
from gtts import gTTS
from pathlib import Path


@dataclass
class LectureTopic:
    name: str
    hook: str
    core_idea: str
    practical_angle: str
    historical_note: str
    modern_connection: str
    reflection: str


TOPICS = deque([
    LectureTopic(
        name="Plate Tectonics",
        hook="Imagine the Earth's crust as a mosaic of slow-dancing plates, each exerting pressure on the others in a geological waltz that never stops.",
        core_idea="Plate tectonics explains how these massive slabs move on the semi-fluid asthenosphere, shaping continents and ocean basins over millions of years.",
        practical_angle="Understanding plate movement helps us interpret patterns of earthquakes, volcanic eruptions, and mountain building, which is vital for hazard planning and resource exploration.",
        historical_note="The theory coalesced in the mid-20th century through the work of scientists like Alfred Wegener, whose continental drift hypothesis laid the foundation, and later evidence from seafloor spreading confirmed the mechanism.",
        modern_connection="Contemporary satellite geodesy measures plate velocities with centimeter precision, allowing scientists to update risk models for tectonically active regions.",
        reflection="When we appreciate plate tectonics, we see Earth's surface not as static, but as an ever-evolving system where patience reveals dramatic transformations.",
    ),
    LectureTopic(
        name="Harlem Renaissance",
        hook="Picture New York's Harlem neighborhood in the 1920s buzzing with jazz, poetry, and visual art that challenged the nation's racial narratives.",
        core_idea="The Harlem Renaissance was a cultural movement where African American artists reshaped American literature and arts by asserting pride in Black identity and experience.",
        practical_angle="Exploring the movement reveals how art becomes a vehicle for political expression and social change, inspiring future civil rights activism.",
        historical_note="Figures like Langston Hughes, Zora Neale Hurston, and Aaron Douglas collaborated across mediums, while publications such as The Crisis amplified their voices to national audiences.",
        modern_connection="The movement's influence echoes in today's discussions about representation in media, the celebration of Black creativity, and the ongoing fight against systemic inequality.",
        reflection="Recognizing the Harlem Renaissance reminds us that cultural flourishing can become a catalyst for broader societal transformation when voices long silenced take center stage.",
    ),
    LectureTopic(
        name="Photosynthesis",
        hook="Consider a leaf as a microscopic factory where sunlight is budgeted like money and invested into chemical bonds that power entire ecosystems.",
        core_idea="Photosynthesis converts light energy into chemical energy by synthesizing glucose from carbon dioxide and water, releasing oxygen as a life-sustaining byproduct.",
        practical_angle="Understanding the light-dependent and light-independent reactions helps in fields from agriculture to renewable energy, informing crop yields and artificial photosynthesis research.",
        historical_note="Discoveries by Jan Ingenhousz and later Melvin Calvin gradually unveiled the stepwise choreography of pigments, electron transport chains, and enzyme-driven carbon fixation.",
        modern_connection="Modern studies leverage spectroscopy and genetic engineering to optimize photosynthetic pathways, with implications for feeding a growing population under climate pressure.",
        reflection="Appreciating photosynthesis reveals the elegance of nature's energy economy and highlights our dependence on fragile green infrastructures.",
    ),
    LectureTopic(
        name="Bayesian Statistics",
        hook="Imagine updating your opinion about the weather the moment you step outside and feel a raindrop—that adaptive mindset is the heart of Bayesian thinking.",
        core_idea="Bayesian statistics treats probability as a measure of belief, updating prior assumptions with new evidence through Bayes' theorem to yield posterior conclusions.",
        practical_angle="This framework is invaluable when data arrive sequentially or are scarce, as in medical diagnostics, machine learning, and risk assessment.",
        historical_note="Named after Thomas Bayes but popularized by Pierre-Simon Laplace, the approach faced skepticism until computational advances in the late twentieth century made it practical.",
        modern_connection="With Markov Chain Monte Carlo and probabilistic programming, Bayesian methods now drive disciplines from autonomous vehicles to natural language processing.",
        reflection="Thinking like a Bayesian encourages intellectual humility, reminding us that certainty grows only by welcoming new evidence.",
    ),
    LectureTopic(
        name="Cellular Respiration",
        hook="Envision every cell as an energy accountant, meticulously breaking down nutrients to pay the ATP bills that keep life running.",
        core_idea="Cellular respiration harvests energy from glucose through glycolysis, the citric acid cycle, and oxidative phosphorylation to produce ATP efficiently.",
        practical_angle="By tracing these pathways, we understand how exercise, diet, and metabolic disorders influence energy availability in cells.",
        historical_note="The sequence of reactions became clear through twentieth-century biochemistry, with Hans Krebs mapping the citric acid cycle and Peter Mitchell proposing chemiosmotic coupling.",
        modern_connection="Current research examines how mitochondrial dynamics and respiratory efficiency impact aging, immune responses, and diseases like cancer.",
        reflection="Appreciating cellular respiration underscores the quiet sophistication of metabolic networks sustaining complex life.",
    ),
    LectureTopic(
        name="Roman Aqueducts",
        hook="Picture ancient engineers plotting the gentle slope of a hidden river in the sky, built from stone and ingenuity to keep a city alive.",
        core_idea="Roman aqueducts transported water over long distances using gravity alone, combining precise surveying with arches, tunnels, and siphons.",
        practical_angle="Studying their design teaches principles of hydraulic engineering, material science, and urban planning that remain relevant today.",
        historical_note="Projects like the Aqua Claudia required vast labor and political will, symbolizing the empire's commitment to public infrastructure and civic life.",
        modern_connection="Their legacy informs modern water management, especially as cities reconsider sustainable, resilient distribution systems.",
        reflection="Roman aqueducts remind us that infrastructure is both a technical marvel and a statement about the societies that build it.",
    ),
])
shuffle_list = list(TOPICS)
shuffle(shuffle_list)
TOPICS.clear()
TOPICS.extend(shuffle_list)

DEFAULT_VOICE = "en"
AUDIO_OUTPUT_FORMAT = "audio/mpeg"
AUDIO_STORAGE_DIR = Path("generated_audio")
AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
LANGUAGES: List[LanguageConfig] = [
    LanguageConfig(name="English", code="en"),
    LanguageConfig(name="Hindi", code="hi"),
    LanguageConfig(name="Gujarati", code="gu"),
]
TRANSLATOR = Translator()


def _rotate_topics() -> LectureTopic:
    topic = TOPICS.popleft()
    TOPICS.append(topic)
    return topic


def _compose_paragraph(*sentences: str) -> str:
    return " ".join(sentences)


def build_lecture(topic: LectureTopic) -> str:
    momentum = _compose_paragraph(topic.hook, topic.core_idea)
    scaffolding = _compose_paragraph(
        "When we zoom in on the mechanics,",
        "we find a sequence of interconnected steps, each relying on the last to make sense of the whole picture.",
        topic.practical_angle,
    )
    historical = _compose_paragraph(
        "Historically,",
        topic.historical_note,
        "These breakthroughs were not sudden revelations but the product of persistent observation and debate.",
    )
    modern = _compose_paragraph(
        "Fast forward to the present,",
        topic.modern_connection,
        "You can see how contemporary tools keep refining what earlier scholars set in motion.",
    )
    application = _compose_paragraph(
        "To ground this in everyday experience,",
        "consider how the concept reaches into classrooms, workplaces, and civic decisions, influencing choices we barely notice.",
        "That relevance transforms abstract knowledge into a guide for action.",
    )
    challenge = _compose_paragraph(
        "Of course, mastering this idea invites challenges,",
        "because each detail opens new questions, forcing us to reconcile theory with what we observe in unpredictable settings.",
        "Those tensions are exactly what make the study vibrant.",
    )
    synthesis = _compose_paragraph(
        "When students grapple with the topic,",
        "they begin to connect disparate facts into a coherent narrative that respects nuance and context.",
        "That narrative empowers them to explain phenomena to others with confidence.",
    )
    reflection = _compose_paragraph(
        topic.reflection,
        "It encourages us to slow our thinking, evaluate the evidence in front of us, and stay curious about what lies beneath the surface.",
    )
    closing = _compose_paragraph(
        "So as we wrap up,",
        "carry the central insight with you and notice how often it appears in headlines, experiments, or historical case studies.",
        "The more you look, the more this idea will reveal layers you may have overlooked before.",
    )
    sentences = [
        topic.hook,
        topic.core_idea,
        historical,
        modern,
        application,
        challenge,
        synthesis,
        reflection,
        closing,
    ]

    summary = sentences[:2]
    return _compose_paragraph(*summary)


def _translate_text(text: str, language_code: str) -> str:
    if language_code == DEFAULT_VOICE:
        return text

    try:
        translation = TRANSLATOR.translate(text, dest=language_code)
        return translation.text
    except Exception as exc:  # pragma: no cover - network dependent
        raise RuntimeError(f"Translation to '{language_code}' failed") from exc


async def _synthesize_audio_file(text: str, voice: str = DEFAULT_VOICE) -> str:
    """Generate MP3 audio using gTTS, persist it, and return the filename."""

    try:
        tts = gTTS(text=text, lang=voice)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
    except Exception as exc:  # pragma: no cover - network dependent
        raise RuntimeError("gTTS synthesis failed") from exc

    filename = f"{uuid.uuid4().hex}.mp3"
    file_path = AUDIO_STORAGE_DIR / filename
    with file_path.open("wb") as audio_file:
        audio_file.write(buffer.getvalue())

    return filename


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/audio", StaticFiles(directory=AUDIO_STORAGE_DIR), name="audio")


@app.get("/lecture")
async def get_lecture(request: Request) -> Dict[str, Any]:
    topic = _rotate_topics()
    lecture_text = build_lecture(topic)
    language_payloads: List[Dict[str, Any]] = []

    for language in LANGUAGES:
        translation_error: str | None = None
        audio_error: str | None = None

        try:
            text_payload = _translate_text(lecture_text, language.code)
        except Exception as exc:  # pragma: no cover - network dependent
            logging.getLogger(__name__).warning("Translation failed for %s: %s", language.name, exc)
            translation_error = "Translation is temporarily unavailable. Showing English text instead."
            text_payload = lecture_text

        audio_payload: Dict[str, Any] | None = None
        try:
            filename = await _synthesize_audio_file(text_payload, voice=language.code)
            audio_url = request.url_for("audio", path=filename)
            audio_payload = {
                "voice": language.code,
                "format": AUDIO_OUTPUT_FORMAT,
                "url": str(audio_url),
                "mime_type": AUDIO_OUTPUT_FORMAT,
            }
        except Exception as exc:  # pragma: no cover - network dependent
            logging.getLogger(__name__).warning("Audio synthesis failed for %s: %s", language.name, exc)
            audio_error = "Text-to-speech is temporarily unavailable."

        language_payloads.append(
            {
                "language": language.name,
                "code": language.code,
                "text": text_payload,
                "audio": audio_payload,
                "translation_error": translation_error,
                "audio_error": audio_error,
            }
        )

    return {
        "topic": topic.name,
        "languages": language_payloads,
    }
