import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export const getGameState = async () => {
    try {
        const response = await axios.get(`${API_URL}/game/state`);
        return response.data;
    } catch (error) {
        console.error("Error fetching game state:", error);
        return null;
    }
};

export const movePiece = async (fromX, fromY, toX, toY) => {
    try {
        const response = await axios.post(`${API_URL}/game/move`, {
            from_x: fromX,
            from_y: fromY,
            to_x: toX,
            to_y: toY
        });
        return response.data;
    } catch (error) {
        console.error("Error moving piece:", error);
        return { success: false, message: error.message };
    }
};

export const resetGame = async () => {
    try {
        const response = await axios.post(`${API_URL}/game/reset`);
        return response.data;
    } catch (error) {
        console.error("Error resetting game:", error);
        return null;
    }
};
