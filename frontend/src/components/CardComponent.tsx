import React from "react";

interface Card{
    id: number;
    name: string;
    email: string;
}

const CardComponent: React.FC<{card: Card}> = ({card}) => {
    if (!card) {
        return (<div>No card</div>);
    }

    if (!card.name || !card.email) {
        return (<div>Invalid card</div>);
    }

    try {
        return (
            <div className="bg-white shadow-lg rounded-lg p-2 mb-2 hover:bg-gray-100">
                <div className="text-sm text-gray-600">Id: {card.id}</div>
                <div className="text-lg font-semibold text-gray-800">{card.name}</div>
                <div className="text-md text-gray-700">{card.email}</div>
            </div>
        );
    } catch (error) {
        console.error("Err rendering card:", error);
        return (<div>Invalid card</div>);
    };
};

export default CardComponent;