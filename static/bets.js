(() => {

    const addButton =
        document.getElementById(
            "add-bet-button"
        );

    const modal =
        document.getElementById(
            "bet-modal"
        );

    const closeButton =
        document.getElementById(
            "bet-modal-close"
        );

    const cancelButton =
        document.getElementById(
            "bet-cancel"
        );

    const form =
        document.getElementById(
            "bet-form"
        );

    const leagueSelect =
        document.getElementById(
            "bet-league"
        );

    const eventSelect =
        document.getElementById(
            "bet-event"
        );

    const typeSelect =
        document.getElementById(
            "bet-type"
        );

    const marketSelect =
        document.getElementById(
            "bet-market"
        );

    const lineField =
        document.getElementById(
            "bet-line-field"
        );

    const lineInput =
        document.getElementById(
            "bet-line"
        );

    const oddsInput =
        document.getElementById(
            "bet-odds"
        );

    const sportsbookSelect =
        document.getElementById(
            "bet-sportsbook"
        );

    const errorBox =
        document.getElementById(
            "bet-form-error"
        );

    const betsList =
        document.getElementById(
            "bets-list"
        );

    const betsMessage =
        document.getElementById(
            "bets-message"
        );


    let loadedEvents = [];
    let loadedMarkets = [];


    function escapeHtml(value) {

        return String(
            value ?? ""
        )
            .replaceAll(
                "&",
                "&amp;"
            )
            .replaceAll(
                "<",
                "&lt;"
            )
            .replaceAll(
                ">",
                "&gt;"
            )
            .replaceAll(
                '"',
                "&quot;"
            )
            .replaceAll(
                "'",
                "&#039;"
            );

    }


    function formatOdds(value) {

        if (
            value === null
            || value === undefined
            || value === ""
        ) {
            return "";
        }

        const number =
            Number(
                value
            );

        if (
            Number.isNaN(
                number
            )
        ) {
            return String(
                value
            );
        }

        if (number > 0) {
            return `+${number}`;
        }

        return `${number}`;

    }


    function formatLine(value) {

        if (
            value === null
            || value === undefined
            || value === ""
        ) {
            return "";
        }

        const number =
            Number(
                value
            );

        if (
            Number.isNaN(
                number
            )
        ) {
            return String(
                value
            );
        }

        if (number > 0) {
            return `+${number}`;
        }

        return `${number}`;

    }


    function sportsbookLabel(value) {

        const labels = {
            draftkings: "DraftKings",
            fanduel: "FanDuel",
            betmgm: "BetMGM",
            caesars: "Caesars",
            bet365: "Bet365",
            circa: "Circa",
            pinnacle: "Pinnacle",
            other: "Other"
        };

        return (
            labels[value]
            || value
            || ""
        );

    }


    function betTypeLabel(value) {

        const labels = {
            spread: "Spread",
            moneyline: "Moneyline",
            total: "Game Total",
            player_prop: "Player Prop"
        };

        return (
            labels[value]
            || value
        );

    }


    function showMessage(
        message,
        isError = false
    ) {

        betsMessage.textContent =
            message;

        betsMessage.hidden =
            false;

        betsMessage.classList.toggle(
            "error",
            isError
        );

        window.setTimeout(
            () => {

                betsMessage.hidden =
                    true;

            },
            3500
        );

    }


    function showFormError(
        message
    ) {

        errorBox.textContent =
            message;

        errorBox.hidden =
            false;

    }


    function clearFormError() {

        errorBox.hidden =
            true;

        errorBox.textContent =
            "";

    }


    function resetForm() {

        form.reset();

        loadedEvents = [];
        loadedMarkets = [];

        eventSelect.innerHTML =
            `
                <option value="">
                    Select a league first...
                </option>
            `;

        eventSelect.disabled =
            true;

        typeSelect.value =
            "";

        typeSelect.disabled =
            true;

        marketSelect.innerHTML =
            `
                <option value="">
                    Select a bet type first...
                </option>
            `;

        marketSelect.disabled =
            true;

        lineField.hidden =
            false;

        lineInput.required =
            true;

        clearFormError();

    }


    function openModal() {

        resetForm();

        modal.hidden =
            false;

        document.body.classList.add(
            "modal-open"
        );

    }


    function closeModal() {

        modal.hidden =
            true;

        document.body.classList.remove(
            "modal-open"
        );

        resetForm();

    }


    async function fetchJson(
        url,
        options = {}
    ) {

        const response =
            await fetch(
                url,
                options
            );

        let payload;

        try {

            payload =
                await response.json();

        }
        catch {

            throw new Error(
                "The server returned an invalid response."
            );

        }

        if (
            !response.ok
            || payload.ok === false
        ) {

            throw new Error(
                payload.error
                || "Request failed."
            );

        }

        return payload;

    }


    async function loadBets() {

        betsList.innerHTML =
            `
                <div class="bets-loading">
                    Loading tracked bets...
                </div>
            `;

        try {

            const payload =
                await fetchJson(
                    "/api/bets"
                );

            renderBets(
                payload.bets || []
            );

        }
        catch (error) {

            betsList.innerHTML =
                `
                    <div class="bets-empty">
                        ${escapeHtml(
                            error.message
                        )}
                    </div>
                `;

        }

    }


    function renderBets(
        bets
    ) {

        if (!bets.length) {

            betsList.innerHTML =
                `
                    <div class="bets-empty">

                        <strong>
                            No tracked bets yet.
                        </strong>

                        <span>
                            Add a bet and it will appear here.
                        </span>

                    </div>
                `;

            return;

        }


        betsList.innerHTML =
            bets.map(
                bet => {

                    const details = [];

                    if (
                        bet.bet_type !==
                        "moneyline"
                    ) {

                        details.push(
                            `Line ${formatLine(
                                bet.line
                            )}`
                        );

                    }

                    if (
                        bet.odds !== null
                        && bet.odds !== undefined
                    ) {

                        details.push(
                            formatOdds(
                                bet.odds
                            )
                        );

                    }

                    if (bet.sportsbook) {

                        details.push(
                            sportsbookLabel(
                                bet.sportsbook
                            )
                        );

                    }


                    return `
                        <article
                            class="bet-card"
                            data-bet-id="${escapeHtml(
                                bet.id
                            )}"
                        >

                            <div class="bet-card-main">

                                <div class="bet-card-topline">

                                    <span class="bet-league-badge">
                                        ${escapeHtml(
                                            bet.league
                                        )}
                                    </span>

                                    <span class="bet-type-badge">
                                        ${escapeHtml(
                                            betTypeLabel(
                                                bet.bet_type
                                            )
                                        )}
                                    </span>

                                </div>


                                <strong class="bet-selection">
                                    ${escapeHtml(
                                        buildBetTitle(
                                            bet
                                        )
                                    )}
                                </strong>


                                <span class="bet-event-name">
                                    ${escapeHtml(
                                        bet.event_name
                                    )}
                                </span>


                                ${
                                    details.length
                                    ? `
                                        <span class="bet-details">
                                            ${escapeHtml(
                                                details.join(
                                                    " • "
                                                )
                                            )}
                                        </span>
                                    `
                                    : ""
                                }

                            </div>


                            <div class="bet-actions">

                                <button
                                    type="button"
                                    class="bet-delete-button"
                                    data-delete-bet="${escapeHtml(
                                        bet.id
                                    )}"
                                >
                                    Delete
                                </button>

                            </div>

                        </article>
                    `;

                }
            ).join(
                ""
            );

    }


    function buildBetTitle(
        bet
    ) {

        if (
            bet.bet_type ===
            "moneyline"
        ) {

            return (
                `${bet.selection} ML`
            );

        }


        if (
            bet.bet_type ===
            "spread"
        ) {

            return (
                `${bet.selection} ` +
                `${formatLine(
                    bet.line
                )}`
            );

        }


        if (
            bet.bet_type ===
            "total"
        ) {

            return (
                `${bet.side.toUpperCase()} ` +
                `${formatLine(
                    bet.line
                )}`
            );

        }


        if (
            bet.bet_type ===
            "player_prop"
        ) {

            const stat =
                bet.stat_name
                ? ` ${bet.stat_name}`
                : "";

            return (
                `${bet.selection}${stat} ` +
                `${bet.side.toUpperCase()} ` +
                `${formatLine(
                    bet.line
                )}`
            );

        }


        return bet.selection;

    }


    async function loadEvents() {

        const league =
            leagueSelect.value;

        loadedEvents = [];
        loadedMarkets = [];

        eventSelect.disabled =
            true;

        typeSelect.disabled =
            true;

        marketSelect.disabled =
            true;

        eventSelect.innerHTML =
            `
                <option value="">
                    Loading games...
                </option>
            `;


        if (!league) {

            eventSelect.innerHTML =
                `
                    <option value="">
                        Select a league first...
                    </option>
                `;

            return;

        }


        clearFormError();


        try {

            const payload =
                await fetchJson(
                    `/api/betting/events?league=${
                        encodeURIComponent(
                            league
                        )
                    }`
                );

            loadedEvents =
                payload.events || [];


            if (!loadedEvents.length) {

                eventSelect.innerHTML =
                    `
                        <option value="">
                            No games with odds found
                        </option>
                    `;

                return;

            }


            eventSelect.innerHTML =
                `
                    <option value="">
                        Select game...
                    </option>
                `
                +
                loadedEvents.map(
                    event => {

                        let suffix = "";

                        if (event.status) {

                            suffix =
                                ` - ${event.status}`;

                        }

                        return `
                            <option
                                value="${escapeHtml(
                                    event.event_id
                                )}"
                            >
                                ${escapeHtml(
                                    event.display_name
                                    + suffix
                                )}
                            </option>
                        `;

                    }
                ).join(
                    ""
                );


            eventSelect.disabled =
                false;

        }
        catch (error) {

            eventSelect.innerHTML =
                `
                    <option value="">
                        Unable to load games
                    </option>
                `;

            showFormError(
                error.message
            );

        }

    }


    async function loadMarkets() {

        const eventId =
            eventSelect.value;

        loadedMarkets = [];

        typeSelect.value =
            "";

        typeSelect.disabled =
            true;

        marketSelect.disabled =
            true;

        marketSelect.innerHTML =
            `
                <option value="">
                    Select a bet type first...
                </option>
            `;


        if (!eventId) {
            return;
        }


        clearFormError();


        try {

            const payload =
                await fetchJson(
                    `/api/betting/events/${
                        encodeURIComponent(
                            eventId
                        )
                    }/markets`
                );

            loadedMarkets =
                payload.markets || [];


            if (!loadedMarkets.length) {

                showFormError(
                    "No supported full-game markets were found for this game."
                );

                return;

            }


            typeSelect.disabled =
                false;

        }
        catch (error) {

            showFormError(
                error.message
            );

        }

    }


    function filterMarkets() {

        const betType =
            typeSelect.value;

        marketSelect.innerHTML =
            `
                <option value="">
                    Select market...
                </option>
            `;


        if (!betType) {

            marketSelect.disabled =
                true;

            return;

        }


        const matching =
            loadedMarkets.filter(
                market =>
                    market.category ===
                    betType
            );


        if (!matching.length) {

            marketSelect.innerHTML =
                `
                    <option value="">
                        No markets available
                    </option>
                `;

            marketSelect.disabled =
                true;

        }
        else {

            marketSelect.innerHTML +=
                matching.map(
                    market => `
                        <option
                            value="${escapeHtml(
                                market.odd_id
                            )}"
                        >
                            ${escapeHtml(
                                market.label
                            )}
                        </option>
                    `
                ).join(
                    ""
                );

            marketSelect.disabled =
                false;

        }


        if (
            betType ===
            "moneyline"
        ) {

            lineField.hidden =
                true;

            lineInput.required =
                false;

            lineInput.value =
                "";

        }
        else {

            lineField.hidden =
                false;

            lineInput.required =
                true;

        }

    }


    function handleMarketChange() {

        const market =
            loadedMarkets.find(
                item =>
                    item.odd_id ===
                    marketSelect.value
            );


        if (!market) {
            return;
        }


        if (
            typeSelect.value !==
            "moneyline"
            && market.current_line !== null
            && market.current_line !== undefined
        ) {

            lineInput.value =
                market.current_line;

        }


        if (
            market.current_odds
            && !oddsInput.value
        ) {

            const numericOdds =
                Number(
                    market.current_odds
                );

            if (
                !Number.isNaN(
                    numericOdds
                )
            ) {

                oddsInput.value =
                    numericOdds;

            }

        }

    }


    async function saveBet(
        event
    ) {

        event.preventDefault();

        clearFormError();


        const selectedEvent =
            loadedEvents.find(
                item =>
                    item.event_id ===
                    eventSelect.value
            );


        const selectedMarket =
            loadedMarkets.find(
                item =>
                    item.odd_id ===
                    marketSelect.value
            );


        if (!selectedEvent) {

            showFormError(
                "Please select a game."
            );

            return;

        }


        if (!selectedMarket) {

            showFormError(
                "Please select a market."
            );

            return;

        }


        if (
            selectedMarket.category !==
            "moneyline"
            && lineInput.value ===
            ""
        ) {

            showFormError(
                "Enter the exact line from your bet."
            );

            return;

        }


        const payload = {
            event_id:
                selectedEvent.event_id,

            event_name:
                selectedEvent.display_name,

            league:
                selectedEvent.league,

            odd_id:
                selectedMarket.odd_id,

            bet_type:
                selectedMarket.category,

            selection:
                selectedMarket.selection,

            side:
                selectedMarket.side,

            stat_id:
                selectedMarket.stat_id,

            stat_name:
                selectedMarket.stat_name,

            line:
                (
                    selectedMarket.category ===
                    "moneyline"
                )
                ? null
                : Number(
                    lineInput.value
                ),

            odds:
                oddsInput.value
                ? Number(
                    oddsInput.value
                )
                : null,

            sportsbook:
                sportsbookSelect.value
        };


        const saveButton =
            document.getElementById(
                "bet-save"
            );

        saveButton.disabled =
            true;

        saveButton.textContent =
            "Saving...";


        try {

            await fetchJson(
                "/api/bets",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


            closeModal();

            await loadBets();

            showMessage(
                "Bet added."
            );

        }
        catch (error) {

            showFormError(
                error.message
            );

        }
        finally {

            saveButton.disabled =
                false;

            saveButton.textContent =
                "Save Bet";

        }

    }


    async function deleteBet(
        betId
    ) {

        const confirmed =
            window.confirm(
                "Delete this tracked bet?"
            );

        if (!confirmed) {
            return;
        }


        try {

            await fetchJson(
                `/api/bets/${
                    encodeURIComponent(
                        betId
                    )
                }`,
                {
                    method:
                        "DELETE"
                }
            );


            await loadBets();

            showMessage(
                "Bet deleted."
            );

        }
        catch (error) {

            showMessage(
                error.message,
                true
            );

        }

    }


    addButton.addEventListener(
        "click",
        openModal
    );


    closeButton.addEventListener(
        "click",
        closeModal
    );


    cancelButton.addEventListener(
        "click",
        closeModal
    );


    modal.addEventListener(
        "click",
        event => {

            if (
                event.target ===
                modal
            ) {

                closeModal();

            }

        }
    );


    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape"
                && !modal.hidden
            ) {

                closeModal();

            }

        }
    );


    leagueSelect.addEventListener(
        "change",
        loadEvents
    );


    eventSelect.addEventListener(
        "change",
        loadMarkets
    );


    typeSelect.addEventListener(
        "change",
        filterMarkets
    );


    marketSelect.addEventListener(
        "change",
        handleMarketChange
    );


    form.addEventListener(
        "submit",
        saveBet
    );


    betsList.addEventListener(
        "click",
        event => {

            const button =
                event.target.closest(
                    "[data-delete-bet]"
                );

            if (!button) {
                return;
            }

            deleteBet(
                button.dataset.deleteBet
            );

        }
    );


    loadBets();

})();