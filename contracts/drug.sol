// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract drug {
  address[] _lab;
  address[] _labmanu;
  string[] _labform;
  string[][] _labfeeds;

  address[] _lotwarehousem;
  uint[] _lotidwarehousem;
  address[] _lotmanuwarehousem;

  address[] _lotmanu;
  uint[] _lotid;
  uint[] _lotpillcount;
  string[] _lotlabform;
  uint[] _lotstatus;

  address[] _waremtransport;
  address[] _transporters;
  uint[] _lotidtransport;

  mapping(string=>bool) labmanus;

  function createTransport(address warem, address transport, uint lotid) public {
    _waremtransport.push(warem);
    _transporters.push(transport);
    _lotidtransport.push(lotid);
  }

  function viewTransport() public view returns(address[] memory,address[] memory,uint[] memory) {
    return(_waremtransport,_transporters,_lotidtransport);
  }

  function createLot(address lotmanu,uint lotid,uint lotpillcount,string memory lotlabform) public {

    _lotmanu.push(lotmanu);
    _lotid.push(lotid);
    _lotpillcount.push(lotpillcount);
    _lotlabform.push(lotlabform);
    _lotstatus.push(1);

  }

  function viewLots() public view returns(address[] memory, uint[] memory,uint[] memory,string[] memory,uint[] memory) {

    return(_lotmanu,_lotid,_lotpillcount,_lotlabform,_lotstatus);
  }

  function allocateLotWareM(address lotmanu,uint lotid, address lotwarehouse) public {
   uint i;

   for(i=0;i<_lotid.length;i++) {
     if(_lotid[i]==lotid) {
       _lotstatus[i]=0;
     }
   }

   _lotmanuwarehousem.push(lotmanu);
   _lotwarehousem.push(lotwarehouse);
   _lotidwarehousem.push(lotid); 

  }

  function viewLotWareM() public view returns (address[] memory,address[] memory, uint[] memory) {
    return (_lotmanuwarehousem,_lotwarehousem,_lotidwarehousem);
  }

  function addLabManufacturer(address lab,address labmanu,string memory labform) public {

    _lab.push(lab);
    labmanus[labform]=true;
    _labmanu.push(labmanu);
    _labform.push(labform);
    _labfeeds.push(["Nice Job"]);
  }

  function viewLabManufacturers() public view returns(address[] memory,address[] memory,string[] memory) {
    return (_lab,_labmanu,_labform);
  }

  function addLabFeedback(uint labform,string memory feed) public {  
    _labfeeds[labform].push(feed);          
  }

  function viewLabFeedback() public view returns(string[][] memory) {
    return (_labfeeds);
  }
}
