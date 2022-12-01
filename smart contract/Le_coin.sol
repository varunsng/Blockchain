pragma solidity ^0.4.11

contract Le_coin {
    uint public max_lecoins = 1000000;
    uint public inr_to_lecoins = 100;
    uint public total_lecoins_bought = 0;

    mapping(address => uint) equity_lecoins;
    mapping(address => uint) equity_inr;

    modifier can_buy_lecoins(uint inr_invested){
        require(inr_invested*inr_to_lecoins+total_lecoins_bought <= max_lecoins);
        _;
    }

    function equity_in_lecoins(address investor) external constant returns (uint){
        return equity_lecoins[investor];
    }

    function equity_in_inr(address investor) external constant returns (uint){
        return equity_inr[investor];
    }

    function buy_lecoins(address investor,uint inr_invested) external
    can_buy_lecoins(inr_invested){
        uint lecoins_bought = inr_invested*inr_to_lecoins;
        equity_lecoins[investor]+=lecoins_bought;
        equity_inr[investor]=equity_lecoins[investor]/100;
        total_lecoins_bought+=lecoins_bought;
    }

    function sell_lecoins(address investor,uint lecoins_sold) external
    {
        equity_lecoins[investor]-=lecoins_sold;
        equity_inr[investor]=equity_lecoins[investor]/100;
        total_lecoins_bought-=lecoins_sold;
    }
}
