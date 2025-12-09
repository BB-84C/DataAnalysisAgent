import streamlit as st


def render_chat_ui():
    st.subheader("Chat Interface")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            (
                "User",
                "Please perform linecut analysis for file '07_15_25_002.sxm'. "
                "Take linecut from (176,176) to (246,211).",
            ),
            (
                "Generating Workflow",
                "Certainly. To perform the requested linecut analysis on `07_15_25_002.sxm`, I will "
                "follow this workflow:\n\n"
                "1. **Open the SXM file & select the topograph channel**\n\n"
                "   * Load `07_15_25_002.sxm` via the `opensxm` operator.\n"
                "   * Use `pnum = 1` to select the **topograph channel** (forward topo).\n"
                "   * This produces a 1x1 figure handle:\n"
                "     `fig_07_15_25_002` (real-space topograph).\n\n"
                "2. **Row-wise background subtraction**\n\n"
                "   * Feed this topograph into the **\"background subtraction along row\"** operator.\n"
                "   * Use `pnum = 2` to apply a polynomial background subtraction line-by-line along the scan rows.\n"
                "   * This removes slow spatial drifts and large-scale height offsets, isolating the relevant modulations.\n"
                "   * Output:\n"
                "     `fig_07_15_25_002_polyback2` (background-subtracted topograph, 1x1 figure).\n\n"
                "3. **Fourier transform of the cleaned topograph**\n\n"
                "   * Take the background-subtracted image and run the **2D Fourier transform** (FT) with `pnum = 3`.\n"
                "   * This converts spatial modulations into **reciprocal-space peaks**, making periodicities easier to quantify.\n"
                "   * Output:\n"
                "     `fig_07_15_25_002_FT` (magnitude FT map, 1x1 figure).\n\n"
                "4. **Extract the linecut in Fourier space**\n\n"
                "   * From the FT figure, extract a linecut using the linecut operator with:\n"
                "     `linecut param = [1, 1, -1, 176, 246, 176, 211]`\n"
                "     where:\n\n"
                "     * The first entries encode internal mode/normalization flags, and\n"
                "     * The coordinates `(176, 176) -> (246, 211)` define the line segment in pixel space along which the intensity profile is taken.\n"
                "   * This yields a 1D intensity profile capturing how the FT amplitude evolves along that direction in **q-space**.\n"
                "   * Output:\n"
                "     `fig_07_15_25_002_Linecut` (linecut figure, 1x1).\n\n"
                "5. **Deliverables for this request**\n"
                "   For your query\n\n"
                "   > \"Please perform linecut analysis for file `07_15_25_002.sxm`, focus on the topograph channel. "
                "Take linecut from (176,176) to (246,211).\"\n\n"
                "   the pipeline above produces the following artifacts:\n\n"
                "   * `fig_07_15_25_002` - raw topograph (pnum = 1)\n"
                "   * `fig_07_15_25_002_polyback2` - row-wise background-subtracted topograph (pnum = 2)\n"
                "   * `fig_07_15_25_002_FT` - Fourier transform of the cleaned topograph (pnum = 3)\n"
                "   * `fig_07_15_25_002_Linecut` - final **linecut** along `(176,176) -> (246,211)` in FT space\n\n"
                "You can now inspect `fig_07_15_25_002_Linecut` to analyze the dominant periodicities and compare "
                "peak positions/intensities along that specific reciprocal-space direction.",
            ),
        ]

    for role, message in st.session_state.chat_history:
        st.markdown(f"**{role}**: {message}")

    user_input = st.text_input(
        "Type your message",
        placeholder="Enter a new request to update the mock workflow",
    )

    if user_input:
        st.session_state.chat_history.append(("User", user_input))
        st.session_state.chat_history.append(
            ("Generating Workflow", "Acknowledged. Generating a workflow preview...")
        )
        st.experimental_rerun()
