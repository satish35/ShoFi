// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.2 <0.9.0;

contract WalletManage{
    address public _owner;

    struct Wallet{
        string user;
        uint balance;
    }

    struct TranscationHistory{
        string username;
        address key;
        uint amount;
    }

    struct Mistake{
        address key;
        uint amount;
    }

    constructor(){
        _owner = msg.sender;
    }

    modifier ownerCheck{
        require(msg.sender == _owner);
        _;
    }

    event Response(bool success);

    receive() external payable {
        mistake.push(Mistake(msg.sender, msg.value));
    }

    fallback() external payable {
        mistake.push(Mistake(msg.sender, msg.value));
    }

    mapping(address => uint) wal;
    mapping(address => mapping(uint => TranscationHistory)) thistory;
    mapping(address => uint) tint;

    Wallet[] createwal;
    Mistake[] mistake;

    function createWallet(string memory _username) public{
        createwal.push(Wallet(_username, msg.sender.balance));
        uint id= createwal.length - 1;
        wal[msg.sender] = id;
    }

    function checkBalance(address _receiver) public view returns(Wallet memory){
        // Wallet memory info=createwal[wal[msg.sender]];
        return createwal[wal[_receiver]];
    }

    function support(address payable _receiver, string memory _username) external payable{
        require(msg.sender.balance >= msg.value, "No balance");
        bool success = _receiver.send(msg.value);
        emit Response(success);
        Wallet storage info_debit=createwal[wal[msg.sender]];
        Wallet storage info_credit=createwal[wal[_receiver]];
        info_debit.balance= info_debit.balance - msg.value;
        info_credit.balance= info_credit.balance - msg.value;
        thistory[msg.sender][tint[msg.sender]] = TranscationHistory(_username, _receiver, msg.value);
        tint[msg.sender] = tint[msg.sender]+1;
    }

    function getTransaction(address _receiver) external view  returns(TranscationHistory[] memory){
        TranscationHistory[] memory transactions = new TranscationHistory[](tint[_receiver]);
        for(uint i=0; i<tint[_receiver]; i++){
            transactions[i] = thistory[_receiver][i];
        }
        return transactions;
    }

    function refundTransfer(address payable _receiver) external ownerCheck returns(bool j){
        for(uint i=0; i<mistake.length; i++){
            Mistake memory info = mistake[i];
            if(_receiver == info.key){
                bool success = _receiver.send(info.amount);
                emit Response(success);
                return true;
            }
            else{
                continue;
            }
        }
        return false;
    } 
}